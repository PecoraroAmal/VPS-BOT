import logging

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

import config
from metrics import get_all_metrics
from formatter import format_status_report

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

_metric_state = {
    "cpu": "normal",
    "ram": "normal",
    "disk": "normal",
}


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(config.TELEGRAM_CHAT_ID):
        logger.warning(f"Comando /status ricevuto da chat non autorizzata: {update.effective_chat.id}")
        return

    metrics = get_all_metrics()
    message = format_status_report(metrics)
    await update.message.reply_text(message, parse_mode="Markdown")

    try:
        await update.message.delete()
    except Exception as e:
        logger.warning(f"Impossibile eliminare il messaggio: {e}")


def _get_level(value, warning, critical):
    if value >= critical:
        return "critical"
    elif value >= warning:
        return "warning"
    else:
        return "normal"


async def check_thresholds(context: ContextTypes.DEFAULT_TYPE):
    global _metric_state
    metrics = get_all_metrics()

    checks = {
        "cpu": (metrics["cpu_percent"], config.CPU_WARNING, config.CPU_CRITICAL, "CPU"),
        "ram": (metrics["ram"]["percent"], config.RAM_WARNING, config.RAM_CRITICAL, "RAM"),
        "disk": (metrics["disk"]["percent"], config.DISK_WARNING, config.DISK_CRITICAL, "Disco"),
    }

    emoji_by_level = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}
    changed = False
    any_critical_or_warning = False

    lines = []
    for key, (value, warning, critical, label) in checks.items():
        new_level = _get_level(value, warning, critical)
        old_level = _metric_state[key]

        if new_level != old_level:
            changed = True
            logger.info(f"{label}: {old_level} -> {new_level} ({value}%)")

        if new_level != "normal":
            any_critical_or_warning = True

        emoji = emoji_by_level[new_level]
        lines.append(f"{emoji} *{label}*: {value}%")

        _metric_state[key] = new_level

    if not changed:
        return

    header = "⚠️ *Attenzione*" if any_critical_or_warning else "✅ *Valori stabili*"
    text = header + "\n\n" + "\n".join(lines)

    await context.bot.send_message(
        chat_id=config.TELEGRAM_CHAT_ID,
        text=text,
        parse_mode="Markdown",
    )


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("status", "Mostra lo stato attuale della VPS"),
    ])
    logger.info("Menu comandi registrato su Telegram")


def main():
    application = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("status", status_command))

    application.job_queue.run_repeating(
        check_thresholds,
        interval=config.CHECK_INTERVAL_SECONDS,
        first=10,
    )

    logger.info("VPS-BOT avviato, in ascolto...")
    application.run_polling()


if __name__ == "__main__":
    main()