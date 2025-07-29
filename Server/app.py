"""
REST API for NEXAPod server coordinator.
"""
import os
import json
import yaml
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from Server.scheduler import Scheduler
from Server.db import DB
from Server.reputation import Reputation
from Infrastruture.output_validator import load_checker


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


def load_config() -> dict:
    """Load and return the server configuration from YAML."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    config = load_config()
    validator = load_checker(config["validator_plugin"])
    quorum = config.get("quorum", 1)
    db = DB(config)
    scheduler = Scheduler(db, config)
    reputation = Reputation(db, config)
    app = FastAPI()

    node_register_counter = Counter(
        "nexapod_node_register_total", "Total number of node registrations"
    )
    job_assigned_counter = Counter(
        "nexapod_job_assigned_total", "Total number of jobs assigned"
    )
    job_result_success_counter = Counter(
        "nexapod_job_result_success_total", "Total number of successful job results"
    )
    job_result_failure_counter = Counter(
        "nexapod_job_result_failure_total", "Total number of failed job results"
    )
    job_submitted_counter = Counter(
        "nexapod_job_submitted_total", "Total number of jobs submitted"
    )

    @app.post("/register")
    async def register_node(request: Request):
        """Verify node signature and register profile."""
        payload = await request.json()
        signature_hex = payload.pop("signature", None)
        public_key_hex = payload.pop("public_key", None)
        if not signature_hex or not public_key_hex:
            raise HTTPException(status_code=400, detail="Missing signature or public_key")
        message = json.dumps(payload, sort_keys=True).encode()
        public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        try:
            public_key.verify(bytes.fromhex(signature_hex), message)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid signature")
        payload["public_key"] = public_key_hex
        node_id = db.register_node(payload)
        node_register_counter.inc()
        return {"node_id": node_id}

    @app.get("/job")
    async def get_job(node_id: str):
        """Assign and return a pending job for the given node."""
        job = scheduler.assign_job(node_id)
        if job:
            job_assigned_counter.inc()
        return job or {}

    @app.post("/result")
    async def submit_result(request: Request):
        """Validate and record a job result, finalize when quorum is reached."""
        result = await request.json()
        try:
            valid = validator(result)
        except Exception as e:
            job_result_failure_counter.inc()
            raise HTTPException(status_code=400, detail=f"Validation error: {e}")
        if not valid:
            job_result_failure_counter.inc()
            raise HTTPException(status_code=400, detail="Result validation failed")
        db.add_vote(result)
        votes = db.count_votes(result["job_id"], result["sha256"])
        if votes >= quorum:
            final = db.get_vote_result(result["job_id"], result["sha256"])
            db.finalize_job(final)
            reputation.update_credits(final)
            job_result_success_counter.inc()
            return {"status": "finalized", "votes": votes}
        return {"status": "vote recorded", "votes": votes}

    @app.post("/jobs")
    async def submit_job(request: Request):
        """Submit a new job to the scheduling queue."""
        job = await request.json()
        db.add_job(job)
        job_submitted_counter.inc()
        return {"status": "job added"}

    @app.get("/metrics")
    async def metrics():
        """Expose Prometheus metrics endpoint."""
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "ok"}

    return app


def main():
    """Run the Uvicorn server."""
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
