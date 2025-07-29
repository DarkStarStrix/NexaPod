import pydantic


class NodeProfile(pydantic.BaseModel):
    cpu: str
    cores: int
    threads: int
    ram_gb: float
    os: str
    gpu: list


class JobRequest(pydantic.BaseModel):
    node_id: str


class JobDescriptor(pydantic.BaseModel):
    schema_version: str
    job_id: str
    type: str
    input_files: list
    docker_image: str
    estimated_flops: float
    tier: int
    requirements: dict
    input_uri: str
    tolerance: float
    credit_rate: float


class JobResult(pydantic.BaseModel):
    job_id: str
    node_id: str
    output: str
    status: str
    timestamp: int
    sha256: str
    signature: str
