FROM python:3.10-slim

# Install git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Install the package in development mode
RUN pip install -e .

# Create cache directory
RUN mkdir -p /root/.cache/huggingface

# Set entrypoint
ENTRYPOINT ["llmcommit"]