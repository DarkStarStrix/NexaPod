import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('nexapod.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Create nodes table
        cursor.execute('''CREATE TABLE IF NOT EXISTS nodes (
                          id TEXT PRIMARY KEY,
                          tier TEXT,
                          profile TEXT)''')
        # Create jobs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                          id TEXT PRIMARY KEY,
                          data TEXT,
                          result TEXT)''')
        # Create logs table
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          job_id TEXT,
                          log TEXT)''')
        self.conn.commit()

    def store_node(self, node):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO nodes VALUES (?,?,?)',
                       (node['id'], node['tier'], str(node['profile'])))
        self.conn.commit()

    def store_job(self, job, result):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO jobs VALUES (?,?,?)',
                       (job['id'], str(job), str(result)))
        self.conn.commit()

    def get_nodes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM nodes')
        return cursor.fetchall()

    def get_jobs(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs')
        return cursor.fetchall()
