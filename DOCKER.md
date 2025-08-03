# Docker Deployment Guide for Legal RAG System

## Overview

This guide explains how to deploy the Legal RAG System using Docker. Docker provides an isolated environment with all necessary dependencies pre-installed, making deployment consistent across different environments.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) (recommended for easier deployment)
- API keys for required services:
  - Voyage AI API key (for embeddings)
  - Pinecone API key (for vector database)
  - Groq API key (optional, for LLM services)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Configure Environment Variables**

   Create a `.env` file in the project root with your API keys:

   ```bash
   # Copy the template
   cp env_template.txt .env
   
   # Edit the .env file with your API keys
   ```

2. **Build and Start the Container**

   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Docker image using the `docker.dockerfile`
   - Start the container with proper volume mapping
   - Expose the API on port 8000

3. **Access the Application**

   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Using Docker Directly

1. **Build the Docker Image**

   ```bash
   docker build -t legal-rag-system -f docker.dockerfile .
   ```

2. **Run the Container**

   ```bash
   docker run -p 8000:8000 \
     -v "$(pwd)/uploads:/app/uploads" \
     -v "$(pwd)/processed:/app/processed" \
     -v "$(pwd)/logs:/app/logs" \
     --env-file .env \
     legal-rag-system
   ```

## Persistent Data

The Docker setup includes volume mapping for three directories:

- `uploads`: For storing uploaded documents
- `processed`: For storing processed document chunks
- `logs`: For application logs

These directories are mapped from your host machine to the container, ensuring data persistence across container restarts.

## Environment Variables

All configuration is done through environment variables in the `.env` file. The Docker container will automatically use these settings.

Key environment variables include:

- `VOYAGE_API_KEY`: Your Voyage AI API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., "us-east-1")
- `PINECONE_INDEX_NAME`: Name of your Pinecone index

See `env_template.txt` for a complete list of configuration options.

## Initializing the Vector Database

After starting the container, you need to initialize the Pinecone index:

```bash
# Using Docker Compose
docker-compose exec legal-rag-app python create_pinecone_index.py

# Or using Docker directly
docker exec -it <container_id> python create_pinecone_index.py
```

## Troubleshooting

### Container Fails to Start

Check the logs for error messages:

```bash
docker-compose logs
```

Common issues include:
- Missing API keys in the `.env` file
- Network connectivity problems
- Insufficient system resources

### API Not Accessible

Ensure the container is running and the port is correctly mapped:

```bash
docker ps
```

You should see the container running with port 8000 mapped.

## Production Deployment Considerations

For production deployments, consider:

1. **Security**: Use Docker secrets or a secure environment variable management system
2. **Scaling**: Deploy behind a load balancer for high availability
3. **Monitoring**: Add health checks and monitoring
4. **Backup**: Implement regular backups of the data volumes