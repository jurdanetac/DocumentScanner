#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = f"{ROOT_DIR}/token"


# Load bot token
try:
    with open(TOKEN_PATH, "r") as file:
        TOKEN = file.read().strip()
except FileNotFoundError:
    print("Bot token file not found")
    sys.exit(1)


# Set logging to console
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Run app
    application.run_polling()
