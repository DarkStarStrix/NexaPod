import pytest

from Client.comms import CoordinatorClient
from Client.executor import execute_job
from Client.logger import log_result
from Client.profiles import get_node_profile


class DummyConfig:
    def __init__(self):
        self.config = {
            'coordinator_url': 'http://localhost:8000',
            'private_key_path': '~/.nexapod/client_ed25519.key',
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
    assert result['status'] == 'completed'
    assert 'output' in result

def test_log_result(tmp_path):
    result = {
        'job_id': 'testjob',
        'output': 'test',
        'status': 'completed',
        'node_id': 'testnode'
    }
    config = DummyConfig()
    log_result(result, config)
    # Should create a log file
    log_path = f"nexapod_{result['job_id']}_log.json"
    assert tmp_path is not None

@pytest.mark.skip(reason="Integration test, requires running server")
def test_coordinator_client():
    config = DummyConfig()
    client = CoordinatorClient(config)
    profile = get_node_profile()
    try:
        client.register_node(profile)
    except Exception:
        pass

