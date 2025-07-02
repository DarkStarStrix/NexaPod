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

