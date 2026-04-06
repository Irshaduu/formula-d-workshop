import subprocess

result = subprocess.run(['venv\\Scripts\\python.exe', 'manage.py', 'test', 'workshop', 'inventory', '--keepdb'], capture_output=True, text=True, encoding='utf-8', errors='replace')

with open('full_errors.txt', 'w', encoding='utf-8') as f:
    f.write(result.stderr)
