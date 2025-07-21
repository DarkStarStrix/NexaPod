from database import Database
from validator import validate_log, generate_signature
import threading
import queue
import hashlib
import time
import ast

job_queue = queue.Queue()

class Scheduler:
    def __init__(self):
        self.db = Database()
        # Track busy nodes to prevent conflicts
        self.node_busy = {}

    @staticmethod
    def submit_job(job):
        job_queue.put(job)
        print(f"Job {job['id']} submitted to the queue.")

    def match_and_schedule(self):
        while True:
            job = job_queue.get()
            node1, node2 = self._find_two_nodes_for_job(job)
            if not node1 or not node2:
                print(f"Not enough verified and available nodes to process job {job['id']}")
                job_queue.task_done()
                continue
            result1 = self._execute_job(job, node1)
            result2 = self._execute_job(job, node2)
            if validate_log(result1) and validate_log(result2):
                if result1['hash'] == result2['hash']:
                    self.db.store_job(job, result1)
                else:
                    print("Hash mismatch detected for job", job['id'])
            else:
                print("Job", job['id'], "failed validation on one or more nodes")
            job_queue.task_done()

    def _find_two_nodes_for_job(self, job):
        # Fetch all registered nodes from the DB
        nodes = self.db.get_nodes()  # Each node: (id, tier, profile)
        verified_available = []
        for record in nodes:
            node_id = record[0]
            if self._verify_node(record) and self._is_node_available(node_id):
                verified_available.append(node_id)
        if len(verified_available) < 2:
            return None, None
        # Return the first two verified and available nodes.
        return verified_available[0], verified_available[1]

    def _verify_node(self, node_record):
        # node_record is a tuple: (id, tier, profile)
        # Check if hardware profile looks valid (i.e., contains an 'os' key)
        try:
            profile = ast.literal_eval(node_record[2])
            if isinstance(profile, dict) and 'os' in profile:
                return True
        except Exception as e:
            print(f"Error verifying node {node_record[0]}: {e}")
        return False

    def _is_node_available(self, node_id):
        # Return True if the node is not currently busy.
        return not self.node_busy.get(node_id, False)

    def _execute_job(self, job, node):
        # Mark node as busy
        self.node_busy[node] = True
        try:
            # Simulate a job execution delay
            time.sleep(1)
            # Generate a hash based on job id and node id to simulate unique execution.
            combined = f"{job['id']}_{node}"
            hash_result = hashlib.sha256(combined.encode()).hexdigest()
            # Generate a valid signature using the job id.
            signature = generate_signature(str(job['id']).encode())
            return {"id": job['id'], "hash": hash_result, "signature": signature}
        finally:
            # Mark node as available after executing the job
            self.node_busy[node] = False

# To start the scheduler in a separate thread:
def start_scheduler():
    scheduler = Scheduler()
    thread = threading.Thread(target=scheduler.match_and_schedule, daemon=True)
    thread.start()
