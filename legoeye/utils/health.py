import psutil

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_str = f.read().strip()
        temp_float = float(temp_str) / 1000.0
    return {
        'temp':temp_float
        }

def get_cpu_usage():
    usage = psutil.cpu_percent(interval=1.0)
    return {
        'usage':float(f"{usage:.2f}")
        }

def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        'total':float(f"{mem.total / (1024**2):.2f}"),
        'available': float(f"{mem.available / (1024**2):.2f}"),
        'used':float(f"{mem.used / (1024**2):.2f}"),
        'free':float(f"{mem.free / (1024**2):.2f}"),
        'usage':float(f"{mem.percent:.2f}")
        }

def get_storage_usage():
    storage = psutil.disk_usage('/')
    return {
        'total':float(f"{storage.total / (1024**3):.2f}"),
        'used':float(f"{storage.used / (1024**3):.2f}"),
        'free':float(f"{storage.free / (1024**3):.2f}"),
        'usage':float(f"{storage.percent:.2f}")
        }
