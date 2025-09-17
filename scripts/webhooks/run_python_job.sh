#!/bin/bash

source /opt/conda/etc/profile.d/conda.sh
conda activate webhook_env
exec python /app/send_webhook.py