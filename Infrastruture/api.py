from flask import Flask, request, jsonify
from node import Node
from tier import Tier
from scheduler import Scheduler
from database import Database

app = Flask(__name__)
scheduler = Scheduler()
db = Database()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    node_id = data.get('id')
    tier_value = data.get('tier')
    node = Node(node_id, Tier(tier_value))
    db.store_node({
        "id": node.id,
        "tier": node.tier.value,
        "profile": node.profile
    })
    return jsonify({"status": "registered", "node": node_id})

@app.route('/submit-job', methods=['POST'])
def submit_job():
    job = request.get_json()
    scheduler.submit_job(job)
    return jsonify({"status": "job submitted", "job_id": job.get('id')})

@app.route('/status', methods=['GET'])
def status():
    # Basic status information; can be extended.
    nodes = db.get_nodes()
    jobs = db.get_jobs()
    return jsonify({"nodes": nodes, "jobs": jobs})

if __name__ == '__main__':
    app.run(debug=True)
