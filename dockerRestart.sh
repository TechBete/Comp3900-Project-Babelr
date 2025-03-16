#! /bin/bash

# Stop and remove all containers, networks, and volumes
echo "Removing Docker containers, networks, and volumes..."
docker-compose down -v

# Rebuild and start the Docker containers
echo "Rebuilding and starting Docker containers..."
docker-compose up --build