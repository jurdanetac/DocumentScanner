#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import os
import sys
from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
)


# Path of project directory root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path of bot token
TOKEN_PATH = f"{ROOT_DIR}/token"


# Load bot token
try:
    with open(TOKEN_PATH, "r") as file:
        TOKEN = file.read().strip()
except FileNotFoundError:
    print("Bot token file not found")
    sys.exit(1)


# Output logs to console
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Create app object
application = ApplicationBuilder().token(TOKEN).build()


# Add decorator functionality for /commands
def command_handler(command):
    def decorator(func):
        handler = CommandHandler(command, func)
        application.add_handler(handler)
        return func

    return decorator


# Respond to /start
@command_handler("start")
async def start_callback(update, context):
    await update.message.reply_text("Welcome to my awesome bot!")


# Respond to photos
async def photo_callback(update, context):
    photo = update.message.photo[-1]
    await update.message.reply_text("I received your image. Metadata:")
    await update.message.reply_text(photo)


# Main program execution
if __name__ == "__main__":
    photo_handler = MessageHandler(filters.PHOTO, photo_callback)
    application.add_handler(photo_handler)

    # Run app
    application.run_polling()

    # Terminate program
    sys.exit(0)
