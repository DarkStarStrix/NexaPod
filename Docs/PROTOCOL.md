# NEXAPod Protocol

## Message Types

### NodeProfile
- cpu: str
- cores: int
- threads: int
- ram_gb: float
- os: str
- gpu: list

### JobDescriptor
- schema_version: str
- job_id: str
- type: str
- input_files: list
- docker_image: str
- estimated_flops: float
- tier: int
- requirements: dict
- input_uri: str
- tolerance: float
- credit_rate: float

### JobResult
- job_id: str
- node_id: str
- output: str
- status: str
- timestamp: int
- sha256: str
- signature: str

---

## Signing & Verification

- All results and credits are signed with Ed25519
- SHA256 hashes are used for result integrity
- Credits are only issued for valid, signed results

---

## Example Flow

1. Node registers with profile
2. Node requests job
3. Node runs job, signs result
4. Node submits result
5. Server verifies, issues credits, logs contribution

