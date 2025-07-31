# NEXAPod API Reference (Alpha v1)

## Overview

The NEXAPod REST API provides core endpoints for node registration, job distribution, and result submission.

**Base URL**: `http://<your-server-ip>:8000`  
**Content-Type**: `application/json`

---

## Endpoints

### Node Management

#### `POST /register`
Registers a new compute node with the coordinator. The node sends its profile, including a unique ID and hardware capabilities.

**Request Body**:
```json
{
  "node_id": "unique_node_identifier_string",
  "profile": {
    "os": "Linux",
    "cpu": "Intel Core i7-12700K",
    "gpu": "NVIDIA RTX 3080",
    "hashes": {
        "runner": "sha256_hash_of_runner.py",
        "weights": "sha256_hash_of_model.safetensors"
    }
  }
}
```

**Response** (200 OK):
```json
{
  "status": "registered",
  "node_id": "unique_node_identifier_string"
}
```

### Job Management

#### `GET /job`
A registered node polls this endpoint to request a compute job.

**Request Headers**:
- `X-Node-ID`: The ID of the node requesting the job.

**Response** (200 OK, with a job):
```json
{
  "job_id": "job_uuid_string",
  "status": "assigned",
  "data": { ...job specific data... },
  "assigned_to": "requesting_node_id"
}
```

**Response** (200 OK, no job available):
```json
{
  "status": "no_job_available"
}
```

#### `POST /result`
A node submits the result of a completed job.

**Request Body**:
```json
{
  "job_id": "job_uuid_string",
  "result": { ...job result data... },
  "node_id": "completing_node_id"
}
```

**Response** (200 OK):
```json
{
  "status": "result_received",
  "job_id": "job_uuid_string"
}
```

### Dashboard Endpoints

#### `GET /nodes`
Provides a list of all registered nodes for display on the dashboard.

**Response** (200 OK):
```json
[
  {
    "id": "node_123",
    "profile": { ... }
  }
]
```

#### `GET /jobs`
Provides a list of all jobs (pending, assigned, completed) for the dashboard.

**Response** (200 OK):
```json
[
  {
    "job_id": "job_abc",
    "status": "completed",
    "assigned_to": "node_123",
    "result": { ... }
  }
]
```
