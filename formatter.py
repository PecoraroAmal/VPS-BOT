def _status_emoji(percent, warning=70, critical=90):
    if percent >= critical:
        return "🔴"
    elif percent >= warning:
        return "🟡"
    else:
        return "🟢"


def format_uptime(uptime):
    parts = []
    if uptime["days"] > 0:
        parts.append(f"{uptime['days']}g")
    if uptime["hours"] > 0:
        parts.append(f"{uptime['hours']}h")
    parts.append(f"{uptime['minutes']}m")
    return " ".join(parts)


def format_top_processes(processes):
    if not processes:
        return "🧠 *Top processi*: dati in fase di calcolo"

    lines = ["🧠 *Top processi*"]
    for i, proc in enumerate(processes, start=1):
        lines.append(
            f"{i}. {proc['name']} — CPU {proc['cpu_percent']}% / "
            f"RAM {proc['ram_percent']}% ({proc['ram_mb']} MB)"
        )
    return "\n".join(lines)


def format_status_report(metrics):
    cpu = metrics["cpu_percent"]
    ram = metrics["ram"]
    disk = metrics["disk"]
    uptime = metrics["uptime"]
    top_processes = metrics["top_processes"]

    message = (
        f"📊 *Stato VPS*\n\n"
        f"{_status_emoji(cpu)} *CPU*: {cpu}%\n"
        f"{_status_emoji(ram['percent'])} *RAM*: {ram['used_gb']} / {ram['total_gb']} GB ({ram['percent']}%)\n"
        f"{_status_emoji(disk['percent'])} *Disco*: {disk['used_gb']} / {disk['total_gb']} GB ({disk['percent']}%)\n"
        f"⏱ *Uptime*: {format_uptime(uptime)}\n\n"
        f"{format_top_processes(top_processes)}"
    )

    return message


if __name__ == "__main__":
    from metrics import get_all_metrics
    print(format_status_report(get_all_metrics()))