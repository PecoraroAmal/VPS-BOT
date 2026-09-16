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


def format_process_chunks(processes, title, empty_message="nessun processo trovato", max_chars=3500):
    """Testo semplice, senza Markdown: i nomi dei processi sono arbitrari
    e possono contenere caratteri (_, *, `, [) che romperebbero il parsing
    Markdown di Telegram e farebbero fallire l'invio del messaggio."""
    if not processes:
        return [f"{title}: {empty_message}"]

    lines = [
        f"{i}. {proc['name']} — CPU {proc['cpu_percent']}% / "
        f"RAM {proc['ram_percent']}% ({proc['ram_mb']} MB)"
        for i, proc in enumerate(processes, start=1)
    ]

    raw_chunks = []
    current = []
    current_len = 0
    for line in lines:
        if current and current_len + len(line) + 1 > max_chars:
            raw_chunks.append(current)
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line) + 1
    if current:
        raw_chunks.append(current)

    total = len(raw_chunks)
    chunks = []
    for i, chunk_lines in enumerate(raw_chunks, start=1):
        header = title if total == 1 else f"{title} (parte {i}/{total})"
        chunks.append(header + "\n" + "\n".join(chunk_lines))

    return chunks


def format_status_report(metrics):
    cpu = metrics["cpu_percent"]
    ram = metrics["ram"]
    disk = metrics["disk"]
    uptime = metrics["uptime"]

    message = (
        f"📊 *Stato VPS*\n\n"
        f"{_status_emoji(cpu)} *CPU*: {cpu}%\n"
        f"{_status_emoji(ram['percent'])} *RAM*: {ram['used_gb']} / {ram['total_gb']} GB ({ram['percent']}%)\n"
        f"{_status_emoji(disk['percent'])} *Disco*: {disk['used_gb']} / {disk['total_gb']} GB ({disk['percent']}%)\n"
        f"⏱ *Uptime*: {format_uptime(uptime)}"
    )

    return message


if __name__ == "__main__":
    import config
    from metrics import get_all_metrics

    metrics = get_all_metrics()
    print(format_status_report(metrics))
    print()
    for chunk in format_process_chunks(metrics["top_processes"], "🏆 Top 5 processi per consumo"):
        print(chunk)
        print(f"--- ({len(chunk)} caratteri) ---")
    print()
    for chunk in format_process_chunks(
        metrics["project_processes"],
        f"📁 Processi in {config.PROJECTS_DIR}",
        empty_message="nessun processo attivo in questa cartella",
    ):
        print(chunk)
        print(f"--- ({len(chunk)} caratteri) ---")