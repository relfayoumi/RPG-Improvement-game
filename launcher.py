import subprocess
import sys
import os

# Path to your main RPG app script
script_path = os.path.join(os.path.dirname(__file__), 'main.py')

# Optional: open with pythonw to hide terminal if GUI-based
subprocess.run([sys.executable, script_path])
