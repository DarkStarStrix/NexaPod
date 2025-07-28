"""
REST API for NEXAPod coordinator.
"""

import os
from flask import Flask, request, jsonify
from .node import Node
from .tier import Tier
from .scheduler import Scheduler
from .database import Database

app = Flask(__name__)
scheduler = Scheduler()
db = Database()

@app.route('/register', methods=['POST'])
def register():
    """Register a new node with its profile and tier."""
    data = request.get_json()
    node = Node(data.get('id'), Tier(data.get('tier')))
    db.store_node({
        "id": node.id,
        "tier": node.tier.value,
        "profile": node.profile
    })
    return jsonify({"status": "registered", "node": node.id})

@app.route('/submit-job', methods=['POST'])
def submit_job():
    """Accept a job submission and enqueue it for scheduling."""
    job = request.get_json()
    scheduler.submit_job(job)
    return jsonify({"status": "job submitted", "job_id": job.get('id')})

@app.route('/status', methods=['GET'])
def status():
    """Return current nodes and jobs stored in the database."""
    return jsonify({
        "nodes": db.get_nodes(),
        "jobs": db.get_jobs()
    })

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    app.run(host=host, port=port)
