import os
import subprocess
import platform

if platform.system() == "Windows":
    activate = ".venv\\Scripts\\activate.bat && python server\\main.py"
    subprocess.call(["cmd.exe", "/c", activate])
else:
    activate = "source .venv/bin/activate && python server/main.py"
    subprocess.call(["bash", "-c", activate])
