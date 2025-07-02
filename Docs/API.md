# NEXAPod API Reference

## REST Endpoints

### POST /register
- Register a new node
- Request: NodeProfile (JSON)
- Response: { node_id: str }

### GET /job?node_id=...
- Poll for a job assignment
- Response: JobDescriptor (JSON) or {}

### POST /result
- Submit a completed job result
- Request: JobResult (JSON)
- Response: { status: "ok" }

### POST /jobs
- Submit a new job to the system
- Request: JobDescriptor (JSON)
- Response: { status: "job added" }

---

## gRPC Service (proto)

See Protocol/nexapod.proto for service and message definitions.

---

## Message Schemas

- NodeProfile
- JobDescriptor
- JobResult

See Protocol/protocol.py for Pydantic models.

