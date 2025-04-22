#! /bin/bash

echo "Do you wish to install Babelr?"
read -p "Are you Sure? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Install containers, networks, packages and volumes
    echo "Installing Babelr Docker containers, networks, packages and volumes..."
    docker-compose up --build

fi
