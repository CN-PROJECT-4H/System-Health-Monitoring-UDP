from config import CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD


def check_alerts(node_id, metrics):
    """
    Check whether system metrics exceed thresholds.
    """

    cpu = metrics["cpu"]
    mem = metrics["mem"]
    disk = metrics["disk"]

    # CPU alert
    if cpu > CPU_THRESHOLD:
        print(f"[ALERT] {node_id} CPU usage = {cpu}% (Threshold {CPU_THRESHOLD}%)")

    # Memory alert
    if mem > MEMORY_THRESHOLD:
        print(f"[ALERT] {node_id} Memory usage = {mem}% (Threshold {MEMORY_THRESHOLD}%)")

    # Disk alert
    if disk > DISK_THRESHOLD:
        print(f"[ALERT] {node_id} Disk usage = {disk}% (Threshold {DISK_THRESHOLD}%)")