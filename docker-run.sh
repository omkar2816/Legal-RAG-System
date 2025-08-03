#!/bin/bash
# Script to build and run the Legal RAG System Docker container

set -e

echo "=== Legal RAG System Docker Deployment ==="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found!"
    echo "Creating .env file from template..."
    cp env_template.txt .env
    echo "⚠️ Please edit the .env file to add your API keys before continuing."
    echo "Press Enter to continue or Ctrl+C to abort..."
    read
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    echo "🐳 Using Docker Compose for deployment"
    echo "Building and starting containers..."
    docker-compose up --build -d
    
    echo ""
    echo "✅ Legal RAG System is now running!"
    echo "📝 API Documentation: http://localhost:8000/docs"
    echo "🔍 Health Check: http://localhost:8000/health"
    echo ""
    echo "To initialize the Pinecone index, run:"
    echo "docker-compose exec legal-rag-app python create_pinecone_index.py"
    echo ""
    echo "To view logs:"
    echo "docker-compose logs -f"
    echo ""
    echo "To stop the application:"
    echo "docker-compose down"
    
else
    echo "🐳 Using Docker for deployment (Docker Compose not found)"
    echo "Building Docker image..."
    docker build -t legal-rag-system -f docker.dockerfile .
    
    echo "Creating necessary directories..."
    mkdir -p uploads processed logs
    
    echo "Starting container..."
    docker run -d --name legal-rag-system \
        -p 8000:8000 \
        -v "$(pwd)/uploads:/app/uploads" \
        -v "$(pwd)/processed:/app/processed" \
        -v "$(pwd)/logs:/app/logs" \
        --env-file .env \
        legal-rag-system
    
    echo ""
    echo "✅ Legal RAG System is now running!"
    echo "📝 API Documentation: http://localhost:8000/docs"
    echo "🔍 Health Check: http://localhost:8000/health"
    echo ""
    echo "To initialize the Pinecone index, run:"
    echo "docker exec -it legal-rag-system python create_pinecone_index.py"
    echo ""
    echo "To view logs:"
    echo "docker logs -f legal-rag-system"
    echo ""
    echo "To stop the application:"
    echo "docker stop legal-rag-system && docker rm legal-rag-system"
fi