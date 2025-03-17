#! /bin/bash

echo "Doing this will remove all Docker Containers, Networks, Volumes and Saved Data"
read -p "Are you Sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Stop and remove all containers, networks, and volumes
    echo "Removing Docker containers, networks, and volumes..."
    docker-compose down -v

    # Rebuild and start the Docker containers
    echo "Rebuilding and starting Docker containers..."
    docker-compose up --build
fi