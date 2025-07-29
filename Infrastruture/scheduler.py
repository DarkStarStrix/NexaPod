"""
Scheduler module for matching and executing jobs on nodes.
"""
import logging
import threading
import queue
import time
import hashlib
import ast
from .database import Database
from .validator import validate_log, generate_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

job_queue = queue.Queue()


class Scheduler:
    """Responsible for job scheduling and execution across nodes."""
    def __init__(self):
        self.db = Database()
        self.node_busy = {}

    @staticmethod
    def submit_job(job: dict):
        """Add a job to the scheduling queue."""
        job_queue.put(job)
        logger.info("Job %s submitted to the queue.", job['id'])

    def match_and_schedule(self):
        """Continuously match jobs to available nodes and schedule execution."""
        while True:
            job = job_queue.get()
            node1, node2 = self._find_two_nodes_for_job()
            if not node1 or not node2:
                logger.warning("Insufficient nodes for job %s.", job['id'])
                job_queue.task_done()
                continue

            result1 = self._execute_job(job, node1)
            result2 = self._execute_job(job, node2)

            if validate_log(result1) and validate_log(result2):
                if result1['hash'] == result2['hash']:
                    self.db.store_job(job, result1)
                else:
                    logger.error("Hash mismatch for job %s.", job['id'])
            else:
                logger.error("Validation failed for job %s.", job['id'])
            job_queue.task_done()

    def _find_two_nodes_for_job(self) -> tuple:
        """Select two available and verified nodes for a given job."""
        records = self.db.get_nodes()
        candidates = [
            rec[0]
            for rec in records
            if self._verify_node(rec) and self._is_node_available(rec[0])
        ]
        if len(candidates) < 2:
            return None, None
        return candidates[0], candidates[1]

    def _verify_node(self, node_record: tuple) -> bool:
        """Verify node profile integrity."""
        try:
            profile = ast.literal_eval(node_record[2])
            return isinstance(profile, dict) and 'os' in profile
        except Exception:
            return False

    def _is_node_available(self, node_id: str) -> bool:
        """Check if the node is currently free."""
        return not self.node_busy.get(node_id, False)

    def _execute_job(self, job: dict, node_id: str) -> dict:
        """Execute a job on a node and return execution metadata."""
        self.node_busy[node_id] = True
        try:
            time.sleep(1)
            combined = f"{job['id']}_{node_id}"
            hash_result = hashlib.sha256(combined.encode()).hexdigest()
            signature = generate_signature(str(job['id']).encode())
            return {"id": job['id'], "hash": hash_result,
                    "signature": signature}
        finally:
            self.node_busy[node_id] = False


def start_scheduler() -> threading.Thread:
    """Initialize and start the scheduler in a background thread."""
    scheduler = Scheduler()
    thread = threading.Thread(target=scheduler.match_and_schedule,
                              daemon=True)
    thread.start()
    return thread


def main():
    """Entry point to start the scheduler module."""
    thread = start_scheduler()
    thread.join()


if __name__ == '__main__':
    main()
