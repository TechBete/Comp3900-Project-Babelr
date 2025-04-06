# User the official Python image from the Docker Hub
# python:3.9-slim has the least amount of vulnerabilities compared to other slim 
# versions of python from docker hub. 
FROM python:3.13-slim

# Set environment variables
ENV FLASK_APP=server.py

# Set python path to include the working directory
ENV PYTHONPATH=/usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file
COPY requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining files into container
COPY . .

# Expose Port
EXPOSE 8016

#define command to run the application
CMD [ "python3", "server.py" ]