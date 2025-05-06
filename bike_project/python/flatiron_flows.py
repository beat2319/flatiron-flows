import subprocess
import os
import pandas as pd

remote_user = os.getenv("user")
remote_host = os.getenv("host")
remote_path = os.getenv("source_db_path")
local_path = os.getenv("local_copy_path")

scp_command_list = [
    "scp",
]

scp_command_list.extend(
    [
        f"{remote_user}@{remote_host}:{remote_path}",
        local_path,
    ]
)

subprocess.run(scp_command_list)
