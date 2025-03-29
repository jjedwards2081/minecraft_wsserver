import os
import subprocess
import platform

venv_folder = ".venv"  # ✅ matches your actual folder name

if platform.system() == "Windows":
    activate = os.path.join(venv_folder, "Scripts", "activate.bat")
    command = f"{activate} && python server\\main.py"
    subprocess.call(["cmd.exe", "/c", command])
else:
    activate = os.path.join(venv_folder, "bin", "activate")
    command = f"source {activate} && python3 server/main.py"
    subprocess.call(["bash", "-c", command])