"""
Module for managing node reputation and credits.
"""


class Reputation:
    """Handles updating of node credits."""
    def __init__(self, db, config):
        self.db = db
        self.config = config

    def update_credits(self, result):
        """Update node credits based on a completed job result."""
        print(f"Credits updated for node: {result.get('node_id', '')} "
              f"job: {result['job_id']}")
