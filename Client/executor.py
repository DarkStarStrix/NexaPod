import tempfile
import docker


def execute_job(job: dict) -> dict:
    """
    Pull Docker image, prepare inputs, run container, and return
    execution result.
    """
    client = docker.from_env()
    image = job['docker_image']
    job_id = job['job_id']
    client.images.pull(image)
    input_dir = tempfile.mkdtemp(prefix=f"nexapod_{job_id}_")
    for input_file in job.get('input_files', []):
        path = f"{input_dir}/{input_file['name']}"
        with open(path, 'wb') as f:
            f.write(input_file['content'])
    output = client.containers.run(
        image,
        volumes={input_dir: {'bind': '/inputs', 'mode': 'rw'}},
        remove=True
    )
    return {
        'job_id': job_id,
        'output': (output.decode() if isinstance(output, bytes)
                   else str(output)),
        'status': 'completed'
    }
