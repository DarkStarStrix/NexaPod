"""
Container runner using Docker to execute jobs in isolation.
"""
import docker
from nexapod.descriptor import JobDescriptor


class ContainerRunner:
    """Executes job containers based on job descriptors."""
    def __init__(self):
        self.client = docker.from_env()

    def run(self, desc: JobDescriptor) -> dict:
        """Run the container and return execution status and logs."""
        volumes = {
            host_path: {'bind': container_path, 'mode': 'rw'}
            for container_path, host_path in desc.outputs.items()
        }
        container = self.client.containers.run(
            desc.image,
            detach=True,
            read_only=True,
            cap_drop=["ALL"],
            security_opt=["no-new-privileges"],
            volumes=volumes
        )
        result = container.wait()
        logs = container.logs().decode()
        return {"status": result.get('StatusCode') == 0, "logs": logs}
