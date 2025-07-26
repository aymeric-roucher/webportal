FROM selenium/standalone-chrome:latest

# Switch to root to install Python and dependencies
USER root

# Install Python 3.13 and system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    curl \
    ca-certificates \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python3.13 as python3
RUN ln -sf /usr/bin/python3.13 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.13 /usr/bin/python

# Install uv for faster Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy all required files for editable install
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN uv sync --frozen

# Copy remaining files
COPY tests/ ./tests/
COPY CLAUDE.md ./

# Set environment variables for headless browser
ENV DISPLAY=:99

# Use the existing seluser from selenium base image and fix permissions
RUN chown -R seluser:seluser /app
USER seluser

# Set uv cache directory to avoid permission issues
ENV UV_CACHE_DIR=/tmp/uv-cache

# Expose port (if needed for web interface)
EXPOSE 8000

# Default command
CMD ["uv", "run", "python", "-m", "src.webportal.get_interactive.main"]