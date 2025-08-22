#!/bin/bash

source /opt/conda/etc/profile.d/conda.sh
conda activate my_env
exec python /usr/src/app/bike_logs.py