#! /bin/bash

# This script is used to uninstall Babelr from a Docker container.

echo "Doing this will remove all Babelr Docker Containers, Networks, Volumes and Saved Data"
read -p "Are you Sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Stop and remove all containers, networks, and volumes
    echo "Removing Babelr Docker containers, networks, and volumes..."
    docker-compose down -v

fi