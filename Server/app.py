import uvicorn
from fastapi import FastAPI, Request
from Server.scheduler import Scheduler
from Server.db import DB
from Server.reputation import Reputation
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def create_app():
    config = load_config()
    db = DB(config)
    scheduler = Scheduler(db, config)
    reputation = Reputation(db, config)
    app = FastAPI()

    @app.post('/register')
    async def register_node(request: Request):
        profile = await request.json()
        node_id = db.register_node(profile)
        return {"node_id": node_id}

    @app.get('/job')
    async def get_job(node_id: str):
        job = scheduler.assign_job(node_id)
        return job or {}

    @app.post('/result')
    async def submit_result(request: Request):
        result = await request.json()
        db.store_result(result)
        reputation.update_credits(result)
        return {"status": "ok"}

    @app.post('/jobs')
    async def submit_job(request: Request):
        job = await request.json()
        db.add_job(job)
        return {"status": "job added"}

    return app

def main():
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    main()

