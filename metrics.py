import time
import psutil

_last_net_check = {
    "time": time.time(),
    "bytes_sent": psutil.net_io_counters().bytes_sent,
    "bytes_recv": psutil.net_io_counters().bytes_recv,
}


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_ram_usage():
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "percent": mem.percent,
    }


def get_disk_usage(path="/"):
    disk = psutil.disk_usage(path)
    return {
        "total_gb": round(disk.total / (1024 ** 3), 2),
        "used_gb": round(disk.used / (1024 ** 3), 2),
        "free_gb": round(disk.free / (1024 ** 3), 2),
        "percent": disk.percent,
    }


def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()

    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
    }


def get_network_usage():
    global _last_net_check

    current = psutil.net_io_counters()
    now = time.time()

    elapsed_seconds = now - _last_net_check["time"]
    sent_mb = (current.bytes_sent - _last_net_check["bytes_sent"]) / (1024 ** 2)
    recv_mb = (current.bytes_recv - _last_net_check["bytes_recv"]) / (1024 ** 2)

    _last_net_check = {
        "time": now,
        "bytes_sent": current.bytes_sent,
        "bytes_recv": current.bytes_recv,
    }

    return {
        "sent_mb": round(sent_mb, 2),
        "recv_mb": round(recv_mb, 2),
        "elapsed_minutes": round(elapsed_seconds / 60, 1),
    }


def get_all_metrics():
    return {
        "cpu_percent": get_cpu_usage(),
        "ram": get_ram_usage(),
        "disk": get_disk_usage(),
        "uptime": get_uptime(),
        "network": get_network_usage(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_metrics(), indent=2))