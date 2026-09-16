import os
import time
import psutil

import config

_process_registry = {}


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


def get_all_processes():
    current_pids = set(psutil.pids())
    for pid in list(_process_registry.keys()):
        if pid not in current_pids:
            del _process_registry[pid]

    for pid in current_pids:
        if pid not in _process_registry:
            try:
                proc = psutil.Process(pid)
                proc.cpu_percent(None)
                _process_registry[pid] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    results = []
    for proc in _process_registry.values():
        try:
            cpu_percent = proc.cpu_percent(None)
            ram_percent = proc.memory_percent()
            ram_mb = proc.memory_info().rss / (1024 ** 2)
            try:
                cwd = proc.cwd()
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                cwd = None
            try:
                cmdline = proc.cmdline()
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                cmdline = []
            results.append({
                "name": proc.name(),
                "pid": proc.pid,
                "cpu_percent": round(cpu_percent, 1),
                "ram_percent": round(ram_percent, 1),
                "ram_mb": round(ram_mb, 1),
                "cwd": cwd,
                "cmdline": cmdline,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    results.sort(key=lambda p: p["cpu_percent"] + p["ram_percent"], reverse=True)
    return results


def get_top_processes(processes, limit=None):
    if limit is None:
        limit = config.TOP_PROCESSES_COUNT
    return processes[:limit]


def _process_in_dir(proc, dir_path):
    cwd = proc.get("cwd")
    if cwd and (cwd == dir_path or cwd.startswith(dir_path + os.sep)):
        return True
    for arg in proc.get("cmdline") or []:
        if arg.startswith(dir_path):
            return True
    return False


def get_project_processes(processes, projects_dir=None):
    if projects_dir is None:
        projects_dir = config.PROJECTS_DIR
    return [p for p in processes if _process_in_dir(p, projects_dir)]


def get_all_metrics():
    processes = get_all_processes()
    return {
        "cpu_percent": get_cpu_usage(),
        "ram": get_ram_usage(),
        "disk": get_disk_usage(),
        "uptime": get_uptime(),
        "top_processes": get_top_processes(processes),
        "project_processes": get_project_processes(processes),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_all_metrics(), indent=2))