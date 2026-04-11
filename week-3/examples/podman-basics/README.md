# Podman Basics: Containerization for Data Science

This example introduces containerization using Podman, focusing on data science workflows and reproducible environments.

## Setup

### Install Podman

**macOS:**
```bash
# Download from podman.io
# Or use the installer from https://podman.io/getting-started/installation
```

**Windows:**
```bash
# Download Podman Desktop from podman.io
# Or use WSL2 with Podman
```

**Verify Installation:**
```bash
podman --version
# Should show: podman version 4.x.x or higher
```

## Overview

You'll learn:
- What containers are and why they matter for data science
- Basic Podman commands
- Running pre-built containers
- Managing containers and images
- Volume mounting for data access
- Building reproducible data science environments

## Template Repository

For a complete containerized data science project, see the **LA Crime Analysis** template:
- GitHub: https://github.com/[instructor-username]/la-crime-analysis
- Features: Multi-stage Dockerfiles, docker-compose, development containers
- Demonstrates: Complete workflow from data fetching to model serving

## What is a Container?

**Think of it like this:**
- **Virtual Machine**: A whole computer inside your computer
- **Container**: Just your application with its dependencies, sharing your computer's OS

**Benefits:**
- Lightweight (MBs not GBs)
- Fast to start (seconds not minutes)
- Consistent across machines
- Easy to share and deploy

## Example 1: Your First Container

### Run a Simple Container

```bash
# Run a hello-world container
podman run hello-world

# What happens:
# 1. Podman looks for 'hello-world' image locally
# 2. Doesn't find it, so downloads from registry
# 3. Creates a container from the image
# 4. Runs the container
# 5. Container prints message and exits
```

**Output:**
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

### Run an Interactive Container

```bash
# Run Ubuntu container with interactive shell
podman run -it ubuntu:22.04 /bin/bash

# You're now inside the container!
# Try some commands:
ls
pwd
cat /etc/os-release

# Exit the container
exit
```

## Example 2: Running Python in a Container

### Run Python Interactively

```bash
# Run Python 3.11 container
podman run -it python:3.11-slim

# You're in a Python REPL
>>> print("Hello from container!")
>>> import sys
>>> print(sys.version)
>>> exit()
```

### Run a Python Script

**Create a script:**
```bash
cat > hello.py << 'EOF'
print("Hello from containerized Python!")
print("This runs in an isolated environment")

import sys
print(f"Python version: {sys.version}")
EOF
```

**Run it in a container:**
```bash
# Mount current directory and run script
podman run -v $(pwd):/app -w /app python:3.11-slim python hello.py
```

**Explanation:**
- `-v $(pwd):/app` - Mount current directory to /app in container
- `-w /app` - Set working directory to /app
- `python:3.11-slim` - Use Python 3.11 image
- `python hello.py` - Command to run

## Example 3: Managing Images

### List Images

```bash
# List all images on your system
podman images

# Output shows:
# REPOSITORY          TAG        IMAGE ID      CREATED       SIZE
# python              3.11-slim  abc123...     2 weeks ago   125 MB
# ubuntu              22.04      def456...     3 weeks ago   77 MB
```

### Pull Images

```bash
# Pull an image without running it
podman pull python:3.11-slim

# Pull specific version
podman pull python:3.11.5-slim

# Pull from different registry
podman pull docker.io/library/python:3.11-slim
```

### Remove Images

```bash
# Remove an image
podman rmi python:3.11-slim

# Remove by ID
podman rmi abc123

# Remove all unused images
podman image prune
```

## Example 4: Managing Containers

### List Containers

```bash
# List running containers
podman ps

# List all containers (including stopped)
podman ps -a

# Output shows:
# CONTAINER ID  IMAGE         COMMAND     CREATED        STATUS      NAMES
# 123abc...     python:3.11   python      2 minutes ago  Up 2 min    cool_name
```

### Start/Stop Containers

```bash
# Run container in background (detached)
podman run -d --name my-python python:3.11-slim sleep 3600

# Stop container
podman stop my-python

# Start stopped container
podman start my-python

# Restart container
podman restart my-python
```

### Remove Containers

```bash
# Remove a stopped container
podman rm my-python

# Force remove running container
podman rm -f my-python

# Remove all stopped containers
podman container prune
```

### Inspect Containers

```bash
# Get detailed information
podman inspect my-python

# Get specific information
podman inspect --format='{{.State.Status}}' my-python
```

## Example 5: Working with Data

### Volume Mounting

**Mount a single directory:**
```bash
# Mount current directory to /data in container
podman run -v $(pwd):/data python:3.11-slim ls /data
```

**Mount multiple directories:**
```bash
# Mount data and output directories
podman run \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  python:3.11-slim \
  ls /app
```

**Read-only mounts:**
```bash
# Mount as read-only
podman run -v $(pwd)/data:/data:ro python:3.11-slim ls /data
```

### Example: Data Analysis in Container

**Create analysis script:**
```bash
cat > analyze.py << 'EOF'
import pandas as pd
import sys

# Read data from mounted directory
df = pd.read_csv('/data/input.csv')

# Perform analysis
summary = df.describe()

# Save results to mounted output directory
summary.to_csv('/output/summary.csv')
print("Analysis complete!")
print(summary)
EOF
```

**Create sample data:**
```bash
mkdir -p data output

cat > data/input.csv << 'EOF'
name,age,score
Alice,25,85
Bob,30,92
Charlie,35,78
EOF
```

**Run analysis in container:**
```bash
podman run \
  -v $(pwd)/data:/data:ro \
  -v $(pwd)/output:/output \
  -v $(pwd)/analyze.py:/app/analyze.py:ro \
  python:3.11-slim \
  sh -c "pip install pandas && python /app/analyze.py"
```

**Check results:**
```bash
cat output/summary.csv
```

## Example 6: Port Mapping

### Run a Web Server

**Create a simple Flask app:**
```bash
cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from container!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
```

**Run with port mapping:**
```bash
# Map container port 5000 to host port 8000
podman run -p 8000:5000 \
  -v $(pwd)/app.py:/app/app.py \
  python:3.11-slim \
  sh -c "pip install flask && python /app/app.py"
```

**Access the app:**
```bash
# Open browser to http://localhost:8000
# Or use curl
curl http://localhost:8000
```

## Example 7: Environment Variables

### Pass Environment Variables

```bash
# Single variable
podman run -e MY_VAR="Hello" python:3.11-slim \
  python -c "import os; print(os.environ.get('MY_VAR'))"

# Multiple variables
podman run \
  -e DATABASE_URL="postgresql://localhost/mydb" \
  -e DEBUG="true" \
  python:3.11-slim \
  python -c "import os; print(os.environ)"

# From file
cat > .env << 'EOF'
DATABASE_URL=postgresql://localhost/mydb
DEBUG=true
API_KEY=secret123
EOF

podman run --env-file .env python:3.11-slim \
  python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

## Example 8: Container Logs

### View Container Output

```bash
# Run container in background
podman run -d --name my-app python:3.11-slim \
  python -c "import time; [print(f'Log {i}') or time.sleep(1) for i in range(100)]"

# View logs
podman logs my-app

# Follow logs (like tail -f)
podman logs -f my-app

# Show last 10 lines
podman logs --tail 10 my-app

# Show logs with timestamps
podman logs -t my-app
```

## Example 9: Executing Commands in Running Containers

### Run Commands in Container

```bash
# Start a long-running container
podman run -d --name my-python python:3.11-slim sleep 3600

# Execute command in running container
podman exec my-python python --version

# Interactive shell in running container
podman exec -it my-python /bin/bash

# Run Python code
podman exec my-python python -c "print('Hello from running container')"
```

## Example 10: Container Networking

### Container Communication

```bash
# Create a network
podman network create my-network

# Run containers on the network
podman run -d --name db --network my-network postgres:15

podman run -d --name app --network my-network \
  -e DATABASE_HOST=db \
  my-app:latest

# Containers can reach each other by name
podman exec app ping db
```

## Common Podman Commands

### Essential Commands

```bash
# Images
podman images              # List images
podman pull <image>        # Download image
podman rmi <image>         # Remove image
podman build -t name .     # Build image from Dockerfile

# Containers
podman ps                  # List running containers
podman ps -a               # List all containers
podman run <image>         # Create and start container
podman start <container>   # Start stopped container
podman stop <container>    # Stop running container
podman rm <container>      # Remove container
podman logs <container>    # View container logs
podman exec <container>    # Execute command in container

# System
podman info                # System information
podman version             # Podman version
podman system prune        # Clean up unused resources
```

### Useful Flags

```bash
-d, --detach              # Run in background
-it                       # Interactive with terminal
-p, --publish             # Port mapping (host:container)
-v, --volume              # Volume mount (host:container)
-e, --env                 # Environment variable
--name                    # Container name
-w, --workdir             # Working directory
--rm                      # Remove container after exit
```

## Podman vs Docker

**Good news:** Most Docker commands work with Podman!

```bash
# Docker command
docker run -it python:3.11-slim

# Podman equivalent
podman run -it python:3.11-slim

# You can even alias podman to docker
alias docker=podman
```

**Key Differences:**
- Podman doesn't require a daemon
- Podman can run rootless (more secure)
- Podman is compatible with Docker images
- Podman commands are nearly identical

## Troubleshooting

### Container Won't Start

```bash
# Check logs
podman logs <container>

# Run interactively to debug
podman run -it <image> /bin/bash
```

### Can't Access Mounted Files

```bash
# Check mount path
podman inspect <container> | grep -A 10 Mounts

# Verify file exists on host
ls -la $(pwd)/file.txt

# Check permissions
ls -l file.txt
```

### Port Already in Use

```bash
# Use different host port
podman run -p 8001:5000 <image>

# Find what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### Out of Disk Space

```bash
# Remove unused images
podman image prune

# Remove unused containers
podman container prune

# Remove everything unused
podman system prune -a
```

## Best Practices

### 1. Use Specific Tags

```bash
# Good: Specific version
podman pull python:3.11.5-slim

# Bad: Latest tag (unpredictable)
podman pull python:latest
```

### 2. Clean Up Regularly

```bash
# Remove stopped containers
podman container prune

# Remove unused images
podman image prune

# Remove everything unused
podman system prune -a
```

### 3. Name Your Containers

```bash
# Good: Named container
podman run --name my-analysis python:3.11-slim

# Bad: Random name
podman run python:3.11-slim
```

### 4. Use Volume Mounts for Data

```bash
# Good: Data persists
podman run -v $(pwd)/data:/data python:3.11-slim

# Bad: Data lost when container stops
podman run python:3.11-slim
```

## Practice Exercises

1. **Run Python container** and execute a simple script
2. **Mount a directory** and access files from container
3. **Run a web server** with port mapping
4. **View logs** from a running container
5. **Execute commands** in a running container

## Data Science Container Patterns

### Pattern 1: Jupyter Notebook Container

```bash
# Run Jupyter in container with data access
podman run -p 8888:8888 \
  -v $(pwd)/notebooks:/home/jovyan/work \
  -v $(pwd)/data:/home/jovyan/data:ro \
  jupyter/scipy-notebook:latest
```

### Pattern 2: Model Training Container

```bash
# Train model with GPU support (if available)
podman run --device nvidia.com/gpu=all \
  -v $(pwd)/data:/data:ro \
  -v $(pwd)/models:/models \
  -v $(pwd)/train.py:/app/train.py:ro \
  tensorflow/tensorflow:latest-gpu \
  python /app/train.py
```

### Pattern 3: API Serving Container

```bash
# Serve model via API
podman run -p 8000:8000 \
  -v $(pwd)/models:/models:ro \
  -v $(pwd)/api.py:/app/api.py:ro \
  -e MODEL_PATH=/models/best_model.pkl \
  python:3.11-slim \
  sh -c "pip install fastapi uvicorn scikit-learn && \
         uvicorn api:app --host 0.0.0.0 --port 8000"
```

See the LA Crime Analysis template for complete examples of these patterns.

## Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Tutorial](https://github.com/containers/podman/blob/main/docs/tutorials/podman_tutorial.md)
- [Podman vs Docker](https://docs.podman.io/en/latest/markdown/podman.1.html)
- [Container Best Practices](https://developers.redhat.com/blog/2016/02/24/10-things-to-avoid-in-docker-containers)
- [LA Crime Analysis Template](https://github.com/[instructor-username]/la-crime-analysis) - Complete containerized project