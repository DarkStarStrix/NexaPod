import tempfile

import docker


def execute_job(job):
    client = docker.from_env()
    image = job['docker_image']
    job.get ('input_files', [])
    job_id = job['job_id']
    client.images.pull(image)
    input_dir = tempfile.mkdtemp(prefix=f"nexapod_{job_id}_")
    for input_file in job.get('input_files', []):
        with open(f"{input_dir}/{input_file['name']}", 'wb') as f:
            f.write(input_file['content'])
    result = client.containers.run(
        image,
        volumes={input_dir: {'bind': '/inputs', 'mode': 'rw'}},
        detach=False,
        remove=True
    )

    return {
        'job_id': job_id,
        'output': result.decode() if isinstance(result, bytes) else str(result),
        'status': 'completed'
    }

