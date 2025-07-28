import time
import requests


class CoordinatorClient:
    """Client for interacting with the coordinator API."""
    def __init__(self, config: dict):
        self.url = config['coordinator_url']
        self.node_id = config.get('node_id')
        self.poll_interval = config.get('poll_interval', 10)

    def register_node(self, profile: dict):
        """Register this node with the coordinator."""
        resp = requests.post(f"{self.url}/register", json=profile)
        if resp.ok:
            self.node_id = resp.json().get('node_id')
        else:
            raise Exception(f"Registration failed: {resp.text}")

    def poll_job(self) -> dict:
        """Poll coordinator for a new job."""
        resp = requests.get(
            f"{self.url}/job",
            params={'node_id': self.node_id}
        )
        if resp.ok and resp.json():
            return resp.json()
        time.sleep(self.poll_interval)
        return None

    def submit_result(self, result: dict) -> dict:
        """Submit execution result back to coordinator."""
        resp = requests.post(f"{self.url}/result", json=result)
        if resp.ok:
            return resp.json()
        raise Exception(f"Result submission failed: {resp.text}")

    def submit_job(self, param: dict) -> dict:
        """Submit a new job to the coordinator."""
        resp = requests.post(f"{self.url}/jobs", json=param)
        if not resp.ok:
            raise Exception(f"Job submission failed: {resp.text}")
        return resp.json()

    def get_status(self) -> dict:
        """Check node status with coordinator."""
        resp = requests.get(
            f"{self.url}/status",
            params={'node_id': self.node_id}
        )
        if resp.ok:
            return resp.json()
        raise Exception(f"Status check failed: {resp.text}")


def get_node_profile() -> dict:
    """Simulate a static node profile for testing."""
    return {
        'cpu': 'Intel Xeon',
        'ram_gb': 32,
        'cores': 16,
        'node_id': 'testnode'
    }


def execute_job(job: dict) -> dict:
    """Simulate job execution for testing."""
    print(f"Executing job {job['job_id']} with image {job['docker_image']}")
    time.sleep(2)
    return {
        'status': 'completed',
        'output': f"Output of job {job['job_id']}"
    }


def log_result(result: dict):
    """Simulate logging of a job result."""
    log_file = f"nexapod_{result['job_id']}_log.json"
    with open(log_file, 'w') as f:
        f.write(str(result))
    print(f"Result logged to {log_file}")
