FROM python:3.11

ARG project_root=/src

RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry_user  && \
    groupadd -g 999 docker && \
    usermod -aG docker poetry_user&& \
    mkdir ${project_root} /scan_dir

COPY src/requirements.txt ${project_root}

RUN pip install --upgrade pip && \
    pip install -r ${project_root}/requirements.txt

COPY src/base_files_full_history_compressed.json src/docker_image_stigs.json ${project_root}

# Copy rest of application
COPY src/ ${project_root}

WORKDIR ${project_root}

CMD python -u main.py "/scan_dir"