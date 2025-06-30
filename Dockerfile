# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install Node.js and npm. Note: This installs the default Node.js version available in the Debian repository.
# For a specific Node.js version, consider using a multi-stage build or NodeSource PPA.
RUN apt-get update && apt-get install -y nodejs npm

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Build React frontend
WORKDIR /app/static/frontend
RUN npm install

# Set REACT_APP_API_BASE_URL as a build argument
ARG REACT_APP_API_BASE_URL

# Set REACT_APP_API_BASE_URL as an environment variable
ENV REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL}

# Build React frontend with the specified API base URL
RUN CI=true REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL npm run build

# Back to root directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application using Gunicorn
CMD exec gunicorn --bind :$PORT --log-level debug app:app
