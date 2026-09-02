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


def format_elapsed(minutes):
    if minutes < 60:
        return f"{minutes}m"
    hours = round(minutes / 60, 1)
    return f"{hours}h"


def format_status_report(metrics):
    cpu = metrics["cpu_percent"]
    ram = metrics["ram"]
    disk = metrics["disk"]
    uptime = metrics["uptime"]
    network = metrics["network"]

    message = (
        f"📊 *Stato VPS*\n\n"
        f"{_status_emoji(cpu)} *CPU*: {cpu}%\n"
        f"{_status_emoji(ram['percent'])} *RAM*: {ram['used_gb']} / {ram['total_gb']} GB ({ram['percent']}%)\n"
        f"{_status_emoji(disk['percent'])} *Disco*: {disk['used_gb']} / {disk['total_gb']} GB ({disk['percent']}%)\n"
        f"🌐 *Rete* ({format_elapsed(network['elapsed_minutes'])}): "
        f"↑ {network['sent_mb']} MB / ↓ {network['recv_mb']} MB\n"
        f"⏱ *Uptime*: {format_uptime(uptime)}"
    )

    return message


if __name__ == "__main__":
    from metrics import get_all_metrics
    print(format_status_report(get_all_metrics()))