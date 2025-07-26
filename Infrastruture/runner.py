import docker
from nexapod.descriptor import JobDescriptor  # updated import after reorganizing

class ContainerRunner:
    def __init__(self):
        self.client = docker.from_env()

    def run(self, desc: JobDescriptor) -> dict:
        # pull image, mount inputs/outputs, enforce resource limits
        volumes = {
            host_path: {'bind': container_path, 'mode': 'rw'}
            for container_path, host_path in desc.outputs.items()
        }
        container = self.client.containers.run(
            desc.image,
            command=None,
            volumes=volumes,
            detach=True,
            read_only=True,  # enforce minimal write access
            cap_drop=["ALL"],  # drop all Linux capabilities
            security_opt=["no-new-privileges"]  # prevent privilege escalation
        )
        result = container.wait()
        logs = container.logs().decode()
        return {"status": result['StatusCode'] == 0, "logs": logs}
