# Creating a python base with shared environment variables
FROM python:3.11 AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ARG project_root=/server

# Install and upgrade pip and poetry
RUN pip install --upgrade pip poetry

# Copy Python requirements here to cache them and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --only main --no-root && \
    mkdir ${project_root}

WORKDIR ${project_root}
# Copy gunicorn config file
COPY ./gunicorn_conf.py ${project_root}/
# Copy and give permissions for docker entrypoint
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Create user with the name poetry and give permissions to project_root dir
RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry && \
    chown poetry:poetry ${project_root}

# Copy rest of application
COPY . ${project_root}/

# Run as poetry user
USER poetry

ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD [ "gunicorn", "--worker-class uvicorn.workers.UvicornWorker", "--config ./gunicorn_conf.py", "server:app"]
