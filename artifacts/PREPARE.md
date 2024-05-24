# Prepare base files hashes

This manifest describes the process of parsing official Docker repository and extracting base files hashes using patterns

## Get started

Firstly, clone official docker repo-info [repository](https://github.com/docker-library/repo-info)

```shell
git clone https://github.com/docker-library/repo-info.git
```

## Run parser

Now fill all required variables in `get_base_files_full_history.py` script:

* repo_info_path - path to cloned docker repository
* base_files_path - where to save base files hashes json
* base_files_compressed_path - where to save compressed version of base files hashes json

Run script and wait until it finish parsing docker git history (make take time, as the initial commit is at 2016 year)
