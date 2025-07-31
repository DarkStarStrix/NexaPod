"""
Database layer for NEXAPod server coordinator.
"""
import sqlite3
import os
import json


class DB:
    """Handles persistence of nodes, jobs, results, and votes."""
    def __init__(self, config):
        """Initialize database connection and ensure tables exist."""
        self.db_path = config.get("db_path", "nexapod.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        """Create tables for nodes, jobs, results, and votes if they do not exist."""
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS nodes (
            node_id TEXT PRIMARY KEY,
            profile TEXT
        )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            job TEXT,
            assigned_node TEXT,
            status TEXT
        )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS results (
            job_id TEXT,
            node_id TEXT,
            result TEXT
        )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS votes (
            job_id TEXT,
            sha256 TEXT,
            node_id TEXT,
            result TEXT
        )"""
        )
        self.conn.commit()

    def register_node(self, profile):
        """Register a new node profile and return its generated node_id."""
        node_id = os.urandom(8).hex()
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO nodes (node_id, profile) VALUES (?, ?)",
            (node_id, json.dumps(profile))
        )
        self.conn.commit()
        return node_id

    def add_job(self, job):
        """Insert a new job with pending status."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO jobs (job_id, job, assigned_node, status) "
            "VALUES (?, ?, ?, ?)",
            (job["job_id"], json.dumps(job), None, "pending")
        )
        self.conn.commit()

    def assign_job(self, node_id):
        """Assign the first pending job to the given node."""
        c = self.conn.cursor()
        c.execute(
            "SELECT job_id, job FROM jobs WHERE status = ? LIMIT 1",
            ("pending",)
        )
        row = c.fetchone()
        if row:
            job_id, job_json = row
            c.execute(
                "UPDATE jobs SET assigned_node = ?, status = ? WHERE job_id = ?",
                (node_id, "assigned", job_id)
            )
            self.conn.commit()
            return json.loads(job_json)
        return None

    def store_result(self, result):
        """Store job result and mark the job as completed."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO results (job_id, node_id, result) VALUES (?, ?, ?)",
            (result["job_id"], result.get("node_id", ""), json.dumps(result))
        )
        c.execute(
            "UPDATE jobs SET status = ? WHERE job_id = ?",
            ("completed", result["job_id"])
        )
        self.conn.commit()

    def add_vote(self, result):
        """Record a vote for a job result from a node."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO votes (job_id, sha256, node_id, result) "
            "VALUES (?, ?, ?, ?)",
            (result["job_id"], result["sha256"], result.get("node_id", ""),
             json.dumps(result))
        )
        self.conn.commit()

    def count_votes(self, job_id, sha256):
        """Count distinct votes for a given job_id and hash."""
        c = self.conn.cursor()
        c.execute(
            "SELECT COUNT(DISTINCT node_id) FROM votes "
            "WHERE job_id = ? AND sha256 = ?",
            (job_id, sha256)
        )
        row = c.fetchone()
        return row[0] if row else 0

    def get_vote_result(self, job_id, sha256):
        """Retrieve the recorded result for a job and hash."""
        c = self.conn.cursor()
        c.execute(
            "SELECT result FROM votes "
            "WHERE job_id = ? AND sha256 = ? LIMIT 1",
            (job_id, sha256)
        )
        row = c.fetchone()
        return json.loads(row[0]) if row else None

    def finalize_job(self, result):
        """Finalize a job by storing its final result."""
        self.store_result(result)

    def get_node_profile(self, node_id):
        """Retrieve stored node profile for a given node_id."""
        c = self.conn.cursor()
        c.execute(
            "SELECT profile FROM nodes WHERE node_id = ?",
            (node_id,)
        )
        row = c.fetchone()
        return json.loads(row[0]) if row else None

    def get_pending_jobs(self):
        """Return a list of (job_id, job dict) for all pending jobs."""
        c = self.conn.cursor()
        c.execute(
            "SELECT job_id, job FROM jobs WHERE status = ?",
            ("pending",)
        )
        rows = c.fetchall()
        return [(job_id, json.loads(job_json)) for job_id, job_json in rows]

    def get_all_jobs(self):
        """Return a list of all jobs."""
        c = self.conn.cursor()
        c.execute(
            "SELECT job_id, job, assigned_node, status FROM jobs"
        )
        rows = c.fetchall()
        return [
            {
                "job_id": row[0],
                "job": json.loads(row[1]),
                "assigned_node": row[2],
                "status": row[3],
            }
            for row in rows
        ]

    def assign_job_to_node(self, job_id, node_id):
        """Mark a job as assigned to a specific node."""
        c = self.conn.cursor()
        c.execute(
            "UPDATE jobs SET assigned_node = ?, status = ? WHERE job_id = ?",
            (node_id, "assigned", job_id)
        )
        self.conn.commit()
