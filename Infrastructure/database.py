"""
Database access layer for NEXAPod coordinator.
"""

import sqlite3


class Database:
    """Handles persistence of nodes, jobs, and logs."""
    def __init__(self, path: str = "nexapod.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        """Create tables for nodes, jobs, and logs if they do not exist."""
        cursor = self.conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS nodes (
               id TEXT PRIMARY KEY,
               tier TEXT,
               profile TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS jobs (
               id TEXT PRIMARY KEY,
               data TEXT,
               result TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS logs (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               job_id TEXT,
               log TEXT)"""
        )
        self.conn.commit()

    def store_node(self, node: dict):
        """Insert or update a node record."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO nodes VALUES (?,?,?)",
            (node["id"], node["tier"], str(node["profile"]))
        )
        self.conn.commit()

    def store_job(self, job: dict, result: dict):
        """Insert or update a job record with its result."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO jobs VALUES (?,?,?)",
            (job["id"], str(job), str(result))
        )
        self.conn.commit()

    def get_nodes(self) -> list:
        """Retrieve all stored nodes."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM nodes")
        return cursor.fetchall()

    def get_jobs(self) -> list:
        """Retrieve all stored jobs."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM jobs")
        return cursor.fetchall()
