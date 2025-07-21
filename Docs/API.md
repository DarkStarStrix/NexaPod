# NEXAPod API Reference

## Overview

The NEXAPod REST API provides endpoints for node registration, job submission, status monitoring, and credit management. All endpoints use JSON for request/response bodies and include comprehensive error handling.

**Base URL**: `http://localhost:5000` (development)  
**API Version**: `v1`  
**Content-Type**: `application/json`  
**Authentication**: Ed25519 signatures (future), API keys (MVP)

## Core Endpoints

### Node Management

#### POST /register
Register a new compute node with the system.

**Request Body**:
```json
{
  "id": "node_12345",
  "tier": "CONSUMER_GPU",
  "profile": {
    "os": "Linux",
    "os_version": "Ubuntu 22.04",
    "processor": "Intel Core i7-12700K",
    "cores": 12,
    "threads": 20,
    "ram_gb": 32,
    "gpu": [
      {
        "model": "NVIDIA RTX 3080",
        "memory_gb": 10
      }
    ],
    "storage_gb": 500,
    "network_mbps": 1000
  },
  "public_key": "ed25519_public_key_hex",
  "capabilities": ["docker", "gpu_compute", "large_memory"]
}
```

**Response** (200 OK):
```json
{
  "status": "registered",
  "node_id": "node_12345",
  "assigned_tier": "CONSUMER_GPU",
  "reputation_score": 1.0,
  "registration_time": "2024-01-01T12:00:00Z"
}
```

**Response** (400 Bad Request):
```json
{
  "error": "INVALID_PROFILE",
  "message": "Missing required field: processor",
  "details": {
    "missing_fields": ["processor"],
    "provided_fields": ["os", "cores", "ram_gb"]
  }
}
```

#### GET /nodes
List all registered nodes (admin endpoint).

**Query Parameters**:
- `tier` (optional): Filter by node tier
- `status` (optional): Filter by node status (available, busy, offline)
- `limit` (optional): Maximum number of results (default: 100)

**Response** (200 OK):
```json
{
  "nodes": [
    {
      "id": "node_12345",
      "tier": "CONSUMER_GPU", 
      "status": "available",
      "reputation": 0.95,
      "last_seen": "2024-01-01T12:00:00Z",
      "jobs_completed": 142,
      "credits_earned": 1250.5
    }
  ],
  "total_count": 1,
  "available_count": 1
}
```

#### GET /nodes/{node_id}
Get detailed information about a specific node.

**Response** (200 OK):
```json
{
  "id": "node_12345",
  "tier": "CONSUMER_GPU",
  "profile": { /* full profile object */ },
  "status": "available",
  "reputation": 0.95,
  "statistics": {
    "jobs_completed": 142,
    "jobs_failed": 3,
    "total_compute_hours": 876.5,
    "credits_earned": 1250.5
  },
  "last_seen": "2024-01-01T12:00:00Z",
  "registration_time": "2023-12-01T08:30:00Z"
}
```

### Job Management

#### POST /submit-job
Submit a new computational job to the system.

**Request Body**:
```json
{
  "id": "job_001",
  "title": "Protein Folding Simulation",
  "description": "AlphaFold prediction for novel protein sequence",
  "docker_image": "nexapod/alphafold:2.3.0",
  "compute_estimate": 1000000000,
  "requirements": {
    "min_tier": "CONSUMER_GPU",
    "min_memory_gb": 8,
    "min_storage_gb": 5,
    "gpu_required": true,
    "timeout_seconds": 3600
  },
  "input_files": ["sequence.fasta", "params.json"],
  "input_uri": "s3://nexapod-inputs/job_001/",
  "output_path": "/results/",
  "validation": {
    "redundancy_factor": 2,
    "tolerance": 0.01
  },
  "credits": {
    "rate": 1.0,
    "max_budget": 100.0
  },
  "metadata": {
    "submitter": "researcher_alice",
    "priority": "normal",
    "tags": ["protein_folding", "alphafold"]
  }
}
```

**Response** (202 Accepted):
```json
{
  "status": "job submitted",
  "job_id": "job_001", 
  "queue_position": 3,
  "estimated_start_time": "2024-01-01T12:05:00Z",
  "estimated_completion_time": "2024-01-01T13:05:00Z"
}
```

#### GET /jobs/{job_id}
Get detailed status of a specific job.

**Response** (200 OK):
```json
{
  "id": "job_001",
  "status": "executing",
  "progress": 0.65,
  "assigned_nodes": ["node_12345", "node_67890"],
  "start_time": "2024-01-01T12:05:30Z",
  "estimated_completion": "2024-01-01T13:05:30Z",
  "resources_used": {
    "cpu_hours": 8.5,
    "gpu_hours": 2.1,
    "memory_gb_hours": 64.0
  },
  "intermediate_results": {
    "checkpoints": 3,
    "last_update": "2024-01-01T12:45:00Z"
  }
}
```

#### GET /jobs
List jobs with filtering and pagination.

**Query Parameters**:
- `status` (optional): Filter by job status  
- `submitter` (optional): Filter by submitter
- `limit` (optional): Maximum results (default: 50)
- `offset` (optional): Pagination offset

**Response** (200 OK):
```json
{
  "jobs": [
    {
      "id": "job_001",
      "title": "Protein Folding Simulation", 
      "status": "executing",
      "progress": 0.65,
      "submitter": "researcher_alice",
      "created_at": "2024-01-01T12:00:00Z",
      "credits_allocated": 85.5
    }
  ],
  "pagination": {
    "total": 156,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### System Status

#### GET /status
Get overall system health and statistics.

**Response** (200 OK):
```json
{
  "system": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 86400
  },
  "nodes": {
    "total": 42,
    "available": 38,
    "busy": 4,
    "offline": 0
  },
  "jobs": {
    "queued": 12,
    "executing": 7,
    "completed_today": 156,
    "failed_today": 2
  },
  "compute": {
    "total_flops": "2.5 TFLOPS",
    "active_flops": "1.8 TFLOPS",
    "utilization_percent": 72
  },
  "credits": {
    "total_issued": 15420.5,
    "total_pending": 342.8,
    "average_rate": 12.5
  }
}
```

#### GET /metrics
Prometheus-compatible metrics endpoint.

**Response** (200 OK):
```
# HELP nexapod_nodes_total Total number of registered nodes
# TYPE nexapod_nodes_total gauge
nexapod_nodes_total{tier="CPU"} 15
nexapod_nodes_total{tier="CONSUMER_GPU"} 25
nexapod_nodes_total{tier="HPC"} 2

# HELP nexapod_jobs_total Total number of jobs by status
# TYPE nexapod_jobs_total counter
nexapod_jobs_total{status="completed"} 1247
nexapod_jobs_total{status="failed"} 23
```

### Credit System

#### GET /credits/{node_id}
Get credit balance and transaction history for a node.

**Response** (200 OK):
```json
{
  "node_id": "node_12345",
  "current_balance": 1250.5,
  "total_earned": 1385.0,
  "total_spent": 134.5,
  "transactions": [
    {
      "id": "tx_789abc",
      "type": "earned",
      "amount": 14.5,
      "job_id": "job_001",
      "timestamp": "2024-01-01T13:05:30Z",
      "description": "Job completion bonus"
    }
  ],
  "earning_rate_24h": 125.5,
  "ranking": 15
}
```

#### POST /credits/transfer
Transfer credits between nodes (future feature).

**Request Body**:
```json
{
  "from_node": "node_12345",
  "to_node": "node_67890", 
  "amount": 50.0,
  "memo": "Payment for collaborative computation",
  "signature": "ed25519_signature"
}
```

### Administrative Endpoints

#### GET /admin/logs
Retrieve system logs (admin only).

**Query Parameters**:
- `level` (optional): Log level filter (debug, info, warn, error)
- `since` (optional): ISO timestamp for log start time
- `component` (optional): Filter by system component

#### POST /admin/maintenance
Put system into maintenance mode.

**Request Body**:
```json
{
  "mode": "maintenance",
  "message": "System upgrade in progress",
  "estimated_duration_minutes": 30
}
```

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": {
      "field": "additional_context",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    "request_id": "req_123456"
  }
}
```

### Common Error Codes

| HTTP Status | Error Code            | Description                                 |
|-------------|-----------------------|---------------------------------------------|
| 400         | `INVALID_REQUEST`     | Malformed request body or parameters        |
| 401         | `UNAUTHORIZED`        | Missing or invalid authentication           |
| 403         | `FORBIDDEN`           | Insufficient permissions                    |
| 404         | `NOT_FOUND`           | Resource does not exist                     |
| 409         | `CONFLICT`            | Resource conflict (e.g., duplicate node ID) |
| 422         | `VALIDATION_ERROR`    | Request validation failed                   |
| 429         | `RATE_LIMITED`        | Too many requests                           |
| 500         | `INTERNAL_ERROR`      | Server-side error                           |
| 503         | `SERVICE_UNAVAILABLE` | System in maintenance mode                  |

## Authentication & Security

### API Key Authentication (MVP)

Include API key in request headers:
```
Authorization: Bearer your_api_key_here
```

### Ed25519 Signature Authentication (Future)

1. Generate message signature:
```python
message = canonical_json(request_body)
signature = node_private_key.sign(message.encode())
```

2. Include in headers:
```
X-Node-ID: node_12345
X-Signature: hex_encoded_signature
X-Timestamp: unix_timestamp
```

### Rate Limiting

| Endpoint      | Rate Limit            |
|---------------|-----------------------|
| `/register`   | 10 per hour per IP    |
| `/submit-job` | 100 per hour per user |
| `/status`     | 1000 per hour per IP  |
| `/jobs/*`     | 500 per hour per user |

## SDK Examples

### Python Client

```python
import requests
from nexapod_client import NexaPodClient

# Initialize client
client = NexaPodClient(
    base_url="http://localhost:5000",
    api_key="your_api_key"
)

# Register node
profile = client.get_node_profile()
response = client.register_node(profile)

# Submit job
job = {
    "id": "my_job_001",
    "docker_image": "tensorflow/tensorflow:latest",
    "requirements": {"min_memory_gb": 8}
}
response = client.submit_job(job)

# Check status
status = client.get_job_status("my_job_001")
```

### cURL Examples

```bash
# Register node
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{"id": "node_001", "tier": "CPU", "profile": {...}}'

# Submit job  
curl -X POST http://localhost:5000/submit-job \
  -H "Content-Type: application/json" \
  -d '{"id": "job_001", "docker_image": "hello-world"}'

# Get system status
curl http://localhost:5000/status
```

## Integration Patterns

### Webhook Notifications (Future)

Configure webhooks to receive job status updates:

```json
{
  "webhook_url": "https://your-service.com/nexapod-webhook",
  "events": ["job.completed", "job.failed", "node.offline"],
  "secret": "webhook_signature_secret"
}
```

### Streaming API (Future)

WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:5000/stream');
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  // Handle real-time job/node updates
};
```

---

*This API reference covers the current implementation.*  
*For message schemas, see [PROTOCOL.md](PROTOCOL.md).*  
*For system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).*  
*For complete documentation, see [Doc.md](Doc.md).*
