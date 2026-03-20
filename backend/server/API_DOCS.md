# VoiceFlow API Documentation

The VoiceFlow Backend is built with FastAPI and follows RESTful standards.

## Base URL
`http://localhost:8001`

## Voice Processing
`POST /voice/process`
- **Request**: `{ "transcription": "string" }`
- **Response**: `{ "action": "string", "entity_type": "string", "data": {}, "audio_response": "string" }`

## Entities
All entities support standard CRUD:
- `/tasks`
- `/workers`
- `/inventory`
- `/shifts`
- `/attendance`
- `/quality-checks`
- `/equipment`
- `/safety-incidents`

## Authentication (Demo Tier)
Current version allows open access for hackathon demonstration. JWT implementation available in `auth_old.py`.

## Compliance
Every request is logged via the `audit_logger.py` into the `audit_logs` table.
