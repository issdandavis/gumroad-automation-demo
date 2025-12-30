#!/bin/bash
set -e

echo "Setting up Unified AI Platform..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create environment files
if [ ! -f bridge-api/.env ]; then
    cp bridge-api/.env.example bridge-api/.env
    echo "Created bridge-api/.env - please configure your settings"
fi

if [ ! -f evolution-framework/.env ]; then
    echo "BRIDGE_API_URL=http://localhost:3001" > evolution-framework/.env
    echo "Created evolution-framework/.env"
fi

# Start services
echo "Starting services with Docker Compose..."
docker-compose -f deployment/docker-compose.prod.yml up -d

echo "Waiting for services to start..."
sleep 10

# Health check
echo "Checking system health..."
curl -f http://localhost:3001/health || { echo "Health check failed. Check logs with: docker-compose logs"; exit 1; }

echo "Unified AI Platform is running!"
echo "Bridge API: http://localhost:3001"
echo "Evolution Framework: http://localhost:5000"
echo "Health Status: http://localhost:3001/health"
