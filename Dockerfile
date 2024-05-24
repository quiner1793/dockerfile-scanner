# Use a specific version to ensure consistency
FROM python:3.11-slim

# Set argument for project root directory
ARG project_root=/src

# Create user and groups, and necessary directories
RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry_user && \
    groupadd -g 999 docker && \
    usermod -aG docker poetry_user && \
    mkdir -p ${project_root} /scan_dir /artifacts /scap-content

# Switch to the created user
USER poetry_user

# Copy dependency file first to leverage Docker cache
COPY --chown=poetry_user:poetry_user src/requirements.txt ${project_root}

# Install dependencies in a single layer
RUN pip install --no-cache-dir -r ${project_root}/requirements.txt

# Copy necessary files and directories
COPY --chown=poetry_user:poetry_user artifacts/base_files_full_history_compressed.json /artifacts/base_files_full_history_compressed.json
COPY --chown=poetry_user:poetry_user scap-content/ /scap-content/
COPY --chown=poetry_user:poetry_user src/ ${project_root}

# Set working directory
WORKDIR ${project_root}

# Specify the user and command to run the application
CMD ["python", "-u", "main.py", "/scan_dir"]
