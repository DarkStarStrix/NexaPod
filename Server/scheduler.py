import threading

class Scheduler:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.lock = threading.Lock()

    def assign_job(self, node_id):
        with self.lock:
            return self.db.assign_job(node_id)
