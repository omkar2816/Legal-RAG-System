# Authentication in Legal RAG API

This document explains how to use the Bearer Token Authentication implemented in the Legal RAG API.

## Overview

The Legal RAG API uses JWT (JSON Web Token) based authentication to secure API endpoints. This authentication method provides a stateless, token-based security mechanism that is widely used in modern web applications and APIs.

## Authentication Flow

1. **Obtain a Token**: Send a POST request to the `/admin/token` endpoint with your credentials
2. **Use the Token**: Include the token in the Authorization header of your requests
3. **Token Expiration**: Tokens expire after a configurable time period (default: 30 minutes)

## Getting a Token

To obtain an authentication token, send a POST request to the `/admin/token` endpoint with your username and password:

```bash
curl -X POST "http://localhost:8000/admin/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

The response will contain the access token:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Using the Token

To access protected endpoints, include the token in the Authorization header of your requests:

```bash
curl -X GET "http://localhost:8000/admin/stats" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Protected Endpoints

The following endpoints require authentication:

- `/query/ask` - Ask questions about legal documents
- `/ingest/upload` - Upload documents to the system
- `/admin/stats` - Get system statistics
- `/admin/config` - Get system configuration
- `/admin/documents/{doc_id}` - Delete documents

## Public Endpoints

The following endpoints are public and do not require authentication:

- `/` - Root endpoint
- `/admin/health` - Health check endpoint
- `/admin/token` - Token generation endpoint

## Configuration

Authentication can be configured using the following environment variables:

- `JWT_SECRET_KEY` - Secret key used to sign JWT tokens
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time in minutes (default: 30)
- `ENABLE_AUTH` - Enable/disable authentication (default: true)
- `ADMIN_USERNAME` - Admin username (default: admin)
- `ADMIN_PASSWORD` - Admin password (default: password)

## Security Recommendations

1. **Change Default Credentials**: Always change the default admin username and password
2. **Use Strong Secret Key**: Set a strong, unique JWT_SECRET_KEY
3. **HTTPS**: Always use HTTPS in production to encrypt token transmission
4. **Token Expiration**: Set an appropriate token expiration time

## Example Code

See the `examples/auth_example.py` file for a complete example of how to authenticate with the API using Python.