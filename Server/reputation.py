class Reputation:
    def __init__(self, db, config):
        self.db = db
        self.config = config

    def update_credits(self, result):
        # MVP: just print, real logic would update a ledger
        print(f"Credits updated for node: {result.get('node_id', '')} job: {result['job_id']}")

