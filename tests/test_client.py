import pytest
import threading
import time
import os
import json

from flask import Flask, request, jsonify

from Client.comms import CoordinatorClient
from Client.executor import execute_job
from Client.logger import log_result
from Client.profiles import get_node_profile


# Minimal test server to simulate the backend
def create_test_server():
    app = Flask(__name__)

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        # Echo back node_id with 200 OK
        return jsonify({"status": "registered",
                        "node": data.get("node_id")}), 200

    @app.route('/submit-job', methods=['POST'])
    def submit_job():
        data = request.get_json()
        # Echo back job submission
        return jsonify({"status": "job submitted",
                        "job_id": data.get("job_id")}), 200

    @app.route('/status', methods=['GET'])
    def status():
        return jsonify({"status": "ok"}), 200

    return app


# Fixture to start the test server in a separate thread
@pytest.fixture(scope="module", autouse=True)
def start_test_server():
    app = create_test_server()
    server_thread = threading.Thread(target=app.run,
                                     kwargs={'port': 8000}, daemon=True)
    server_thread.start()
    # Allow server time to start
    time.sleep(1)
    yield
    # Normally, teardown logic would go here (if needed)
    # ...existing code...


class DummyConfig:
    def __init__(self):
        self.config = {
            'coordinator_url': 'http://localhost:8000',
            'private_key_path': os.path.expanduser(
                '~/.nexapod/client_ed25519.key'),
            'node_id': 'testnode',
            'poll_interval': 1
        }

    def __getitem__(self, k):
        return self.config[k]

    def get(self, k, default=None):
        return self.config.get(k, default)


def test_get_node_profile():
    profile = get_node_profile()
    assert 'cpu' in profile
    assert 'ram_gb' in profile
    assert isinstance(profile['cores'], int)


def test_execute_job():
    job = {
        'docker_image': 'hello-world',
        'job_id': 'testjob',
        'input_files': []
    }
    result = execute_job(job)
    # Expect simulated execution to return a dictionary with 'status'
    # and 'output'
    assert result['status'] == 'completed'
    assert 'output' in result


def test_log_result(tmp_path):
    result = {
        'job_id': 'testjob',
        'output': 'test output',
        'status': 'completed',
        'node_id': 'testnode'
    }
    config = DummyConfig()
    log_result(result, config)
    # Verify that the expected log file is created
    log_file = f"nexapod_{result['job_id']}_log.json"
    assert os.path.exists(log_file)
    # Clean up
    os.remove(log_file)


def test_integration():
    """Robust integration test covering node registration, job submission,
       status checking, and result logging."""
    config = DummyConfig()
    client = CoordinatorClient(config)
    profile = get_node_profile()

    # 1. Register node (expect 200 OK)
    response = client.register_node(profile)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "registered"
    assert data.get("node") == config['node_id']

    # 2. Submit a job
    job = {
        'docker_image': 'hello-world',
        'job_id': 'integration_test_job',
        'input_files': []
    }
    response = client.submit_job(job)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "job submitted"
    assert data.get("job_id") == job['job_id']

    # 3. Poll for job status (simulate waiting for worker processing)
    time.sleep(2)
    response = client.get_status()
    assert response.status_code == 200
    status_data = response.json()
    assert status_data.get("status") == "ok"

    # 4. Simulate logging the job result
    job_result = {
        'job_id': job['job_id'],
        'output': 'integration test output',
        'status': 'completed',
        'node_id': config['node_id']
    }
    log_result(job_result, config)
    log_file = f"nexapod_{job_result['job_id']}_log.json"
    # Wait briefly to ensure file write
    time.sleep(0.5)
    assert os.path.exists(log_file)
    # Load and check log content
    with open(log_file, 'r') as f:
        logged_data = json.load(f)
    assert logged_data.get("status") == "completed"
    # Clean up log file
    os.remove(log_file)

    # Integration test passes if all responses are 200 OK
    # ...existing code...


@pytest.mark.skip(reason="Integration test that requires external "
                         "dependencies")
def test_coordinator_client():
    config = DummyConfig()
    client = CoordinatorClient(config)
    profile = get_node_profile()
    try:
        response = client.register_node(profile)
        assert response.status_code == 200
    except Exception:
        pytest.skip("Coordinator server not available")
    try:
        response = client.submit_job({
            'docker_image': 'hello-world',
            'job_id': 'testjob',
            'input_files': []
        })
        assert response.status_code == 200
    except Exception:
        pytest.skip("Coordinator server not available for job submission")
    try:
        response = client.get_status()
        assert response.status_code == 200
    finally:
        # Cleanup if needed
        pass
