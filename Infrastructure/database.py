"""
Database access layer for NEXAPod coordinator.
"""

import sqlite3
import json


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
               profile TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS jobs (
               job_id TEXT PRIMARY KEY,
               status TEXT,
               assigned_to TEXT,
               data TEXT,
               result TEXT)"""
        )
        self.conn.commit()

    def store_node(self, node_id: str, profile: str):
        """Insert or update a node record."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO nodes (id, profile) VALUES (?,?)",
            (node_id, profile)
        )
        self.conn.commit()

    def store_job(self, job: dict):
        """Insert or update a job record."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO jobs (job_id, status, assigned_to, data, result) VALUES (?,?,?,?,?)",
            (job["job_id"], job["status"], job["assigned_to"], json.dumps(job.get("data")), json.dumps(job.get("result")))
        )
        self.conn.commit()

    def update_job_result(self, job_id: str, result: str):
        """Update a job with its result and set status to completed."""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE jobs SET result = ?, status = 'completed' WHERE job_id = ?",
            (result, job_id)
        )
        self.conn.commit()

    def get_nodes(self) -> list:
        """Retrieve all stored nodes."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, profile FROM nodes")
        # Return a list of dicts for easier JSON serialization
        return [{"id": row[0], "profile": json.loads(row[1])} for row in cursor.fetchall()]

    def get_jobs(self) -> list:
        """Retrieve all stored jobs."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT job_id, status, assigned_to, data, result FROM jobs")
        # Return a list of dicts
        return [
            {
                "job_id": row[0],
                "status": row[1],
                "assigned_to": row[2],
                "data": json.loads(row[3]) if row[3] else None,
                "result": json.loads(row[4]) if row[4] else None,
            }
            for row in cursor.fetchall()
        ]
