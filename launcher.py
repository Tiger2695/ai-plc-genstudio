import os
import sys
import subprocess
import webbrowser
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(project_dir, "app.py")

subprocess.Popen(
    [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
    ]
)

time.sleep(3)

webbrowser.open("http://localhost:8501")