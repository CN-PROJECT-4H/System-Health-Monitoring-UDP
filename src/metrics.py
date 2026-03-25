import psutil
import time
import platform

def get_system_metrics():
    """
    Collect overall system metrics
    """

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
    disk_usage = psutil.disk_usage(disk_path).percent
    timestamp = int(time.time())

    return {
        "cpu": cpu_usage,
        "mem": memory_usage,
        "disk": disk_usage,
        "timestamp": timestamp
    }


def get_top_processes(limit=5):

    psutil.cpu_percent(interval=1)  # IMPORTANT

    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            if proc.info['name'] == "System Idle Process":
                continue

            if not proc.info['name']:
                continue

            cpu = proc.cpu_percent(interval=None)

            #  NEW: get disk I/O
            try:
                io = proc.io_counters()
                read_kb = round(io.read_bytes / 1024, 2) if io else 0
                write_kb = round(io.write_bytes / 1024, 2) if io else 0
            except (psutil.AccessDenied, AttributeError):
                read_kb = 0
                write_kb = 0

            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": cpu,
                "memory_percent": proc.info['memory_percent'],
                "read_kb": read_kb,     #  NEW
                "write_kb": write_kb    #  NEW
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # sort by CPU usage
    processes = sorted(processes, key=lambda x: x["cpu_percent"], reverse=True)

    return processes[:limit]