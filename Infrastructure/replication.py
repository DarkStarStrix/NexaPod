"""
Module for job replication strategies.
"""

import asyncio
import hashlib
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Callable, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReplicationStrategy(Enum):
    """Available replication strategies."""
    NONE = "none"
    SIMPLE = "simple"
    CONSENSUS = "consensus"
    CHECKPOINT = "checkpoint"
    REDUNDANT = "redundant"


class ReplicationStatus(Enum):
    """Replication status for jobs."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class JobDescriptor:
    """Job descriptor with replication metadata."""
    id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 1
    needs_replication: bool = False
    replication_strategy: ReplicationStrategy = ReplicationStrategy.SIMPLE
    replication_factor: int = 2
    verification_threshold: float = 0.8
    checksum: Optional[str] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.checksum is None:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for job integrity verification."""
        data = f"{self.id}{self.task_type}{json.dumps(self.payload, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify job data integrity using checksum."""
        return self.checksum == self._calculate_checksum()


@dataclass
class ReplicationResult:
    """Result of a replication operation."""
    job_id: str
    node_id: str
    status: ReplicationStatus
    result_hash: Optional[str] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class ReplicationNode:
    """Represents a compute node for replication."""

    def __init__(self, node_id: str, compute_func: Callable):
        self.node_id = node_id
        self.compute_func = compute_func
        self.is_available = True
        self.load = 0.0
        self.reliability_score = 1.0

    async def execute_job(self, job: JobDescriptor) -> ReplicationResult:
        """Execute job on this node and return result."""
        start_time = time.time()

        try:
            if not self.is_available:
                raise RuntimeError(f"Node {self.node_id} is not available")

            if not job.verify_integrity():
                raise ValueError(f"Job {job.id} failed integrity check")

            # Simulate job execution
            result = await self._simulate_computation(job)
            execution_time = time.time() - start_time

            result_hash = hashlib.sha256(str(result).encode()).hexdigest()

            return ReplicationResult(
                job_id=job.id,
                node_id=self.node_id,
                status=ReplicationStatus.COMPLETED,
                result_hash=result_hash,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Job execution failed on node {self.node_id}: {e}")

            return ReplicationResult(
                job_id=job.id,
                node_id=self.node_id,
                status=ReplicationStatus.FAILED,
                execution_time=execution_time,
                error_message=str(e)
            )

    @staticmethod
    async def _simulate_computation(job: JobDescriptor) -> Any:
        """Simulate computation based on job type."""
        await asyncio.sleep(0.1)  # Simulate processing time

        if job.task_type == "protein_folding":
            return {"conformation": "folded", "energy": -42.5}
        elif job.task_type == "weather_simulation":
            return {"temperature": 23.5, "humidity": 65.2}
        elif job.task_type == "quantum_computation":
            return {"qubits": [0, 1, 0, 1], "entanglement": True}
        else:
            return {"result": f"computed_{job.id}"}


class ConsensusValidator:
    """Validates results using consensus mechanisms."""

    def __init__(self, threshold: float = 0.67):
        self.threshold = threshold

    def validate_results(self, results: List[ReplicationResult]) -> ReplicationResult:
        """Validate results using majority consensus."""
        if not results:
            raise ValueError("No results to validate")
        # Group results by hash
        hash_groups: Dict[str, List[ReplicationResult]] = {}
        for result in results:
            if result.status == ReplicationStatus.COMPLETED and result.result_hash:
                hash_groups.setdefault(result.result_hash, []).append(result)
        if not hash_groups:
            # No successful results
            failed_result = next(
                (r for r in results if r.status == ReplicationStatus.FAILED),
                results[0]
            )
            failed_result.status = ReplicationStatus.FAILED
            return failed_result
        # Find consensus
        total_successful = sum(len(group) for group in hash_groups.values())
        consensus_hash, consensus_results = max(
            hash_groups.items(), key=lambda x: len(x[1])
        )
        consensus_ratio = len(consensus_results) / total_successful
        # Select best result from consensus group
        best_result = min(consensus_results, key=lambda r: r.execution_time)
        if consensus_ratio >= self.threshold:
            best_result.status = ReplicationStatus.VERIFIED
        else:
            best_result.status = ReplicationStatus.COMPLETED
        logger.info(
            f"Consensus reached for job {best_result.job_id}: {consensus_ratio:.2%}"
        )
        return best_result


class Replicator:
    """Performs replication logic for computed jobs."""

    def __init__(self, nodes: Optional[List[ReplicationNode]] = None):
        self.nodes = nodes or []
        self.validator = ConsensusValidator()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.replication_history: Dict[str, List[ReplicationResult]] = {}

    def add_node(self, node: ReplicationNode):
        """Add a replication node."""
        self.nodes.append(node)
        logger.info(f"Added replication node: {node.node_id}")

    def remove_node(self, node_id: str):
        """Remove a replication node."""
        self.nodes = [n for n in self.nodes if n.node_id != node_id]
        logger.info(f"Removed replication node: {node_id}")

    def select_nodes(self, job: JobDescriptor) -> List[ReplicationNode]:
        """Select optimal nodes for job replication."""
        available_nodes = [n for n in self.nodes if n.is_available]
        if len(available_nodes) < job.replication_factor:
            logger.warning(
                f"Insufficient nodes for replication factor {job.replication_factor}"
            )
            return available_nodes
        # Sort by reliability and load
        sorted_nodes = sorted(
            available_nodes,
            key=lambda n: (n.reliability_score, -n.load),
            reverse=True
        )
        return sorted_nodes[:job.replication_factor]

    def replicate(self, job: JobDescriptor) -> bool:
        """Replicate computation based on job descriptor."""
        logger.info(f"Starting replication for job: {job.id}")
        if not job.needs_replication:
            logger.info(f"No replication required for job: {job.id}")
            return True
        try:
            if job.replication_strategy == ReplicationStrategy.SIMPLE:
                return self._simple_replication(job)
            elif job.replication_strategy == ReplicationStrategy.CONSENSUS:
                return self._consensus_replication(job)
            elif job.replication_strategy == ReplicationStrategy.REDUNDANT:
                return self._redundant_replication(job)
            else:
                logger.error(
                    f"Unsupported replication strategy: {job.replication_strategy}"
                )
                return False
        except Exception as e:
            logger.error(f"Replication failed for job {job.id}: {e}")
            return False

    def _simple_replication(self, job: JobDescriptor) -> bool:
        """Simple replication strategy - execute once with backup."""
        selected_nodes = self.select_nodes(job)

        if not selected_nodes:
            logger.error(f"No available nodes for job {job.id}")
            return False

        primary_node = selected_nodes[0]
        backup_nodes = selected_nodes[1:] if len(selected_nodes) > 1 else []

        try:
            # Execute on primary node
            result = asyncio.run(primary_node.execute_job(job))

            if result.status == ReplicationStatus.COMPLETED:
                self.replication_history[job.id] = [result]
                logger.info(f"Simple replication successful for job {job.id}")
                return True

            # Try backup nodes if primary fails
            for backup_node in backup_nodes:
                backup_result = asyncio.run(backup_node.execute_job(job))
                if backup_result.status == ReplicationStatus.COMPLETED:
                    self.replication_history[job.id] = [backup_result]
                    logger.info(f"Backup replication successful for job {job.id}")
                    return True

            logger.error(f"All replication attempts failed for job {job.id}")
            return False

        except Exception as e:
            logger.error(f"Simple replication failed for job {job.id}: {e}")
            return False

    def _consensus_replication(self, job: JobDescriptor) -> bool:
        """Consensus-based replication strategy."""
        selected_nodes = self.select_nodes(job)
        if len(selected_nodes) < 2:
            logger.warning(
                f"Insufficient nodes for consensus replication of job {job.id}"
            )
            return self._simple_replication(job)
        try:
            # Execute on all selected nodes concurrently
            async def run_consensus():
                tasks = [node.execute_job(job) for node in selected_nodes]
                return await asyncio.gather(*tasks, return_exceptions=True)
            results = asyncio.run(run_consensus())
            # Filter out exceptions and failed results
            valid_results = [
                r for r in results
                if isinstance(r, ReplicationResult) and r.status in [
                    ReplicationStatus.COMPLETED, ReplicationStatus.FAILED
                ]
            ]
            if not valid_results:
                logger.error(
                    f"No valid results for consensus replication of job {job.id}"
                )
                return False
            # Validate using consensus
            consensus_result = self.validator.validate_results(valid_results)
            self.replication_history[job.id] = valid_results
            success = consensus_result.status in [
                ReplicationStatus.COMPLETED, ReplicationStatus.VERIFIED
            ]
            if success:
                logger.info(f"Consensus replication successful for job {job.id}")
            else:
                logger.error(f"Consensus replication failed for job {job.id}")
            return success
        except Exception as e:
            logger.error(
                f"Consensus replication failed for job {job.id}: {e}"
            )
            return False

    def _redundant_replication(self, job: JobDescriptor) -> bool:
        """Redundant replication strategy - execute on all available nodes."""
        available_nodes = [n for n in self.nodes if n.is_available]
        if not available_nodes:
            logger.error(
                f"No available nodes for redundant replication of job {job.id}"
            )
            return False
        try:
            async def run_redundant():
                tasks = [node.execute_job(job) for node in available_nodes]
                return await asyncio.gather(*tasks, return_exceptions=True)
            results = asyncio.run(run_redundant())
            valid_results = [
                r for r in results
                if isinstance(r, ReplicationResult)
            ]
            successful_results = [
                r for r in valid_results
                if r.status == ReplicationStatus.COMPLETED
            ]
            self.replication_history[job.id] = valid_results
            if successful_results:
                logger.info(
                    f"Redundant replication successful for job {job.id}: "
                    f"{len(successful_results)}/{len(valid_results)} succeeded"
                )
                return True
            else:
                logger.error(
                    f"Redundant replication failed for job {job.id}: no successful executions"
                )
                return False
        except Exception as e:
            logger.error(f"Redundant replication failed for job {job.id}: {e}")
            return False

    def get_replication_status(self, job_id: str) -> Optional[List[ReplicationResult]]:
        """Get replication history for a job."""
        return self.replication_history.get(job_id)

    def cleanup_history(self, max_age_hours: int = 24):
        """Clean up old replication history."""
        cutoff_time = time.time() - (max_age_hours * 3600)

        for job_id, results in list(self.replication_history.items()):
            if all(r.timestamp < cutoff_time for r in results):
                del self.replication_history[job_id]

        logger.info(f"Cleaned up replication history older than {max_age_hours} hours")


def replicate_data():
    """Function to handle data replication logic."""
    logger.info("Data replication process started.")
    # Here you would implement the actual data replication logic
    # For now, we just log the action
    logger.info("Data replication process completed.")
    return True


def replicate_job(job: JobDescriptor, replicator: Optional[Replicator] = None):
    """Function to handle job replication logic."""
    logger.info(f"Job replication process started for job: {job.id}")

    if replicator is None:
        # Create default replicator with mock nodes
        replicator = Replicator()
        # Add some mock nodes for demonstration
        for i in range(3):
            node = ReplicationNode(f"node_{i}", lambda x: f"result_{i}")
            replicator.add_node(node)

    success = replicator.replicate(job)

    if success:
        logger.info(f"Job replication successful for job: {job.id}")
    else:
        logger.error(f"Job replication failed for job: {job.id}")

    return success


def replicate_jobs(jobs: List[JobDescriptor], replicator: Optional[Replicator] = None):
    """Function to handle replication of multiple jobs."""
    logger.info("Starting replication for multiple jobs.")
    if replicator is None:
        replicator = Replicator()
        # Add mock nodes
        for i in range(5):
            node = ReplicationNode(f"node_{i}", lambda x: f"result_{i}")
            replicator.add_node(node)
    results = []
    for job in jobs:
        result = replicate_job(job, replicator)
        results.append(result)
    successful_count = sum(results)
    logger.info(
        f"Completed replication for {successful_count}/{len(jobs)} jobs successfully."
    )
    return all(results)


# Example usage and testing
def create_demo_jobs() -> List[JobDescriptor]:
    """Create demo jobs for testing."""
    jobs = [
        JobDescriptor(
            id="job_001",
            task_type="protein_folding",
            payload={"protein_sequence": "ACDEFGHIKLMNPQRSTVWY"},
            needs_replication=True,
            replication_strategy=ReplicationStrategy.CONSENSUS,
            replication_factor=3
        ),
        JobDescriptor(
            id="job_002",
            task_type="weather_simulation",
            payload={"region": "northwest", "time_range": "24h"},
            needs_replication=True,
            replication_strategy=ReplicationStrategy.SIMPLE,
            replication_factor=2
        ),
        JobDescriptor(
            id="job_003",
            task_type="quantum_computation",
            payload={"qubits": 8, "algorithm": "shor"},
            needs_replication=True,
            replication_strategy=ReplicationStrategy.REDUNDANT,
            replication_factor=5
        )
    ]
    return jobs


if __name__ == "__main__":
    # Demo usage
    demo_jobs = create_demo_jobs()

    # Create replicator with nodes
    replicator = Replicator()
    for i in range(5):
        node = ReplicationNode(f"compute_node_{i}", lambda x: f"computed_result_{i}")
        node.reliability_score = 0.8 + (i * 0.05)  # Varying reliability
        replicator.add_node(node)

    # Test replication
    print("Testing job replication...")
    for job in demo_jobs:
        success = replicator.replicate(job)
        status = replicator.get_replication_status(job.id)
        print(f"Job {job.id}: {'SUCCESS' if success else 'FAILED'}")
        if status:
            print(f"  Results: {len(status)} executions")
            for result in status:
                print(f"    Node {result.node_id}: {result.status.value}")

    # Cleanup
    replicator.cleanup_history()
    print("Replication history cleaned up.")
    replicate_data()  # Example data replication call
