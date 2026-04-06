import subprocess
res = subprocess.run(['venv\\Scripts\\python.exe', 'manage.py', 'test', 'workshop', 'inventory'], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
