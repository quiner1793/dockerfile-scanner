FROM python:3.11

ARG project_root=/workflow
ARG artifacts_dir=/artifacts
ARG scan_dir=/scan_dir

RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry && \
    mkdir ${project_root} ${scan_dir}

WORKDIR ${project_root}

COPY requirements.txt /${project_root}

RUN pip install --upgrade pip && \
    pip install -r ${project_root}/requirements.txt

COPY base_files_full_history_compressed.json docker_image_stigs.json ${project_root}

# Copy rest of application
COPY main.py ${project_root}

CMD python -u main.py ${scan_dir}
