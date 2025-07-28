"""
Scheduler module for assigning jobs to nodes based on their profile.
"""

import threading


class Scheduler:
    """Assigns pending jobs to nodes."""

    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.lock = threading.Lock()

    def assign_job(self, node_id):
        """Assign the first pending job whose requirements match the node's profile."""
        with self.lock:
            profile = self.db.get_node_profile(node_id)
            for job_id, job in self.db.get_pending_jobs():
                if self._meets_requirements(profile, job.get("requirements", {})):
                    self.db.assign_job_to_node(job_id, node_id)
                    return job
            return None

    def _meets_requirements(self, profile, requirements):
        """Check if node profile satisfies job requirements."""
        for key, value in requirements.items():
            if key not in profile:
                return False
            node_val = profile[key]
            if isinstance(value, (int, float)):
                if node_val < value:
                    return False
            else:
                if value != node_val:
                    return False
        return True
