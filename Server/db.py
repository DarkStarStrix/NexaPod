import sqlite3
import os
import json

class DB:
    def __init__(self, config):
        self.db_path = config.get('db_path', 'nexapod.db')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY,
            profile TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            job TEXT,
            assigned_node TEXT,
            status TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS results (
            job_id TEXT,
            node_id TEXT,
            result TEXT
        )''')
        self.conn.commit()

    def register_node(self, profile):
        node_id = os.urandom(8).hex()
        c = self.conn.cursor()
        c.execute('INSERT INTO nodes (node_id, profile) VALUES (?, ?)', (node_id, json.dumps(profile)))
        self.conn.commit()
        return node_id

    def add_job(self, job):
        c = self.conn.cursor()
        c.execute('INSERT INTO jobs (job_id, job, assigned_node, status) VALUES (?, ?, ?, ?)',
                  (job['job_id'], json.dumps(job), None, 'pending'))
        self.conn.commit()

    def assign_job(self, node_id):
        c = self.conn.cursor()
        c.execute('SELECT job_id, job FROM jobs WHERE status = ? LIMIT 1', ('pending',))
        row = c.fetchone()
        if row:
            job_id, job_json = row
            c.execute('UPDATE jobs SET assigned_node = ?, status = ? WHERE job_id = ?', (node_id, 'assigned', job_id))
            self.conn.commit()
            return json.loads(job_json)
        return None

    def store_result(self, result):
        c = self.conn.cursor()
        c.execute('INSERT INTO results (job_id, node_id, result) VALUES (?, ?, ?)',
                  (result['job_id'], result.get('node_id', ''), json.dumps(result)))
        c.execute('UPDATE jobs SET status = ? WHERE job_id = ?', ('completed', result['job_id']))
        self.conn.commit()

