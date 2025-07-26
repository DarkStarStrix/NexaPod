import logging
from descriptor import JobDescriptor

class Replicator:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def replicate(self, job: JobDescriptor) -> bool:
        """Replicate computation based on job descriptor.
           Returns True if replication was performed.
        """
        logging.info(f"Starting replication for job: {job.id}")
        if getattr(job, "needs_replication", False):
            logging.info("Replication needed, performing replication.")
            # ...existing replication code...
            return True
        else:
            logging.info("Replication not required.")
            return False
