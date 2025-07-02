import psutil
import platform
import subprocess

def get_node_profile():
    profile = {
        'cpu': platform.processor(),
        'cores': psutil.cpu_count(logical=False),
        'threads': psutil.cpu_count(logical=True),
        'ram_gb': round(psutil.virtual_memory().total / 1e9, 2),
        'os': platform.system(),
        'gpu': None
    }
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                               capture_output=True, text=True, check=True)
        gpus = []
        for line in result.stdout.strip().split('\n'):
            name, mem = line.split(',')
            gpus.append({'name': name.strip(), 'memory_gb': float(mem.strip().split()[0]) / 1024})
        profile['gpu'] = gpus
    except Exception:
        profile['gpu'] = []
    return profile

