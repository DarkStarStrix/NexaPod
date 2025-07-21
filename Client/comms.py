import requests
import time

class CoordinatorClient:
    def __init__(self, config):
        self.url = config['coordinator_url']
        self.node_id = config.get('node_id')
        self.poll_interval = config.get('poll_interval', 10)

    def register_node(self, profile):
        resp = requests.post(f"{self.url}/register", json=profile)
        if resp.ok:
            self.node_id = resp.json().get('node_id')
        else:
            raise Exception(f"Registration failed: {resp.text}")

    def poll_job(self):
        resp = requests.get(f"{self.url}/job", params={'node_id': self.node_id})
        if resp.ok and resp.json():
            return resp.json()
        time.sleep(self.poll_interval)
        return None

    def submit_result(self, result):
        resp = requests.post(f"{self.url}/result", json=result)
        if not resp.ok:
            raise Exception(f"Result submission failed: {resp.text}")

    def submit_job(self, param):
        resp = requests.post(f"{self.url}/submit", json=param)
        if not resp.ok:
            raise Exception(f"Job submission failed: {resp.text}")
        return resp.json()

def get_node_profile():
    # Simulated profile data
    return {
        'cpu': 'Intel Xeon',
        'ram_gb': 32,
        'cores': 16,
        'node_id': 'testnode'
    }

def execute_job(job):
    # Simulated job execution
    print(f"Executing job {job['job_id']} with image {job['docker_image']}")
    time.sleep(2)  # Simulate time taken to execute the job
    return {
        'status': 'completed',
        'output': f"Output of job {job['job_id']}"
    }

def log_result(result, config):
    log_file = f"nexapod_{result['job_id']}_log.json"
    with open(log_file, 'w') as f:
        f.write(str(result))
    print(f"Result logged to {log_file}")
