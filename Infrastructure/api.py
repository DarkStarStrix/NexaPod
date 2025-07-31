"""
REST API for NEXAPod coordinator.
"""

import os
import json
from flask import Flask, request, jsonify
from .scheduler import Scheduler
from .database import Database

app = Flask(__name__)
scheduler = Scheduler()
db = Database()


@app.route('/register', methods=['POST'])
def register():
    """Register a new node with its profile."""
    data = request.get_json()
    if not data or 'node_id' not in data or 'profile' not in data:
        return jsonify({"error": "Invalid registration data"}), 400

    node_id = data['node_id']
    profile = data['profile']

    db.store_node(node_id, json.dumps(profile))
    return jsonify({"status": "registered", "node_id": node_id})


@app.route('/job', methods=['GET'])
def get_job():
    """A node requests a job from the scheduler."""
    node_id = request.headers.get('X-Node-ID')
    if not node_id:
        return jsonify({"error": "X-Node-ID header is required"}), 400

    job = scheduler.get_job(node_id)
    if job:
        db.store_job(job)
        return jsonify(job)

    return jsonify({"status": "no_job_available"})


@app.route('/result', methods=['POST'])
def submit_result():
    """A node submits the result of a completed job."""
    data = request.get_json()
    if not data or 'job_id' not in data or 'result' not in data:
        return jsonify({"error": "Invalid result submission"}), 400

    db.update_job_result(data['job_id'], json.dumps(data['result']))
    return jsonify({"status": "result_received", "job_id": data['job_id']})


@app.route('/nodes', methods=['GET'])
def get_nodes():
    """Return a list of all registered nodes."""
    nodes = db.get_nodes()
    return jsonify(nodes)


@app.route('/jobs', methods=['GET'])
def get_jobs():
    """Return a list of all jobs."""
    jobs = db.get_jobs()
    return jsonify(jobs)


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    app.run(host=host, port=port)
