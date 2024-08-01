install:
    #!/bin/bash
    set -exo pipefail
    source /opt/conda/etc/profile.d/conda.sh
    conda env list | grep  $PWD/venv || conda create -y --prefix $PWD/venv python=3.11 pip ipykernel
    conda activate $PWD/venv

    pip install -U -r requirements.txt
    pip install -e .
