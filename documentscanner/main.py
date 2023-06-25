#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import needed third-party libraries
# See requirements.txt for more information

import logging
import os
import shutil
import sys
import time
from pathlib import Path

import cv2
import numpy
from PIL import Image
from telegram import (
    ForceReply,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    constants,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import Scanner

# Path of project directory root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path of images directory
IMG_DIR = f"{ROOT_DIR}/images"
SCANNED_IMG_DIR = f"{ROOT_DIR}/images/scanned"
ORIGINAL_IMG_DIR = f"{ROOT_DIR}/images/original"
# Path of scanned documents
PDF_DIR = f"{ROOT_DIR}/pdf"
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
logger = logging.getLogger(__name__)


async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /about is issued."""
    await update.message.reply_text(
        "Proyecto final\. Programación III N\-612 2023\.\n\n"
        "*Integrantes\:*\n"
        "\- Baez, Samuel\n"
        "\- Mavares, Cesar \n"
        "\- Urdaneta, Juan\n\n"
        "https\:\/\/github\.com\/jurdanetac\/DocumentScanner",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )


def reset_chat(USER: str) -> None:
    """Delete previously sent pictures"""
    shutil.rmtree(f"{ORIGINAL_IMG_DIR}/{USER}", ignore_errors=True)
    shutil.rmtree(f"{SCANNED_IMG_DIR}/{USER}", ignore_errors=True)
    shutil.rmtree(f"{PDF_DIR}/{USER}", ignore_errors=True)
    Path(f"{ORIGINAL_IMG_DIR}/{USER}").mkdir(exist_ok=True)
    Path(f"{SCANNED_IMG_DIR}/{USER}").mkdir(exist_ok=True)
    Path(f"{PDF_DIR}/{USER}").mkdir(exist_ok=True)


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    reset_chat(str(update["message"]["chat"]["id"]))

    Path(IMG_DIR).mkdir(exist_ok=True)
    Path(SCANNED_IMG_DIR).mkdir(exist_ok=True)
    Path(ORIGINAL_IMG_DIR).mkdir(exist_ok=True)

    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!", reply_markup=ForceReply(selective=True)
    )


async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear old pictures stored when the command /reset is issued."""
    reset_chat(str(update["message"]["chat"]["id"]))
    await update.message.reply_html("Reset performed successfully.")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("TODO")


async def photo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to photos"""
    img = await context.bot.get_file(update.message.photo[-1])
    await img.download_to_drive(
        custom_path=f'{ORIGINAL_IMG_DIR}/{str(update["message"]["chat"]["id"])}/{img.file_id}'
    )
    scanned_img = Scanner.scan(
        f'{ORIGINAL_IMG_DIR}/{str(update["message"]["chat"]["id"])}/{img.file_id}'
    )
    scanned_file = Image.fromarray(scanned_img)
    scanned_file_path = f'{SCANNED_IMG_DIR}/{str(update["message"]["chat"]["id"])}/scanned_{img.file_id}.jpeg'
    scanned_file.save(scanned_file_path)
    await context.bot.send_document(
        chat_id=update.message["chat"]["id"],
        document=open(scanned_file_path, "rb"),
        filename=scanned_file_path,
    )


async def pdf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if os.listdir(f'{SCANNED_IMG_DIR}/{str(update["message"]["chat"]["id"])}'):
        images = [
            Image.open(f'{SCANNED_IMG_DIR}/{str(update["message"]["chat"]["id"])}/{f}')
            for f in os.listdir(
                f'{SCANNED_IMG_DIR}/{str(update["message"]["chat"]["id"])}'
            )
        ]
        PDF_NAME = time.strftime("%Y%m%d-%H%M%S") + ".pdf"
        PDF_PATH = f'{PDF_DIR}/{str(update["message"]["chat"]["id"])}/{PDF_NAME}'
        images[0].save(
            PDF_PATH, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )
        await context.bot.send_document(
            chat_id=update.message["chat"]["id"],
            document=open(PDF_PATH, "rb"),
            filename=PDF_NAME,
        )
    else:
        await update.message.reply_html("You have to scan at least 1 document first!")


def main() -> None:
    """Start the bot."""

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(CommandHandler("pdf", pdf_callback))
    application.add_handler(CommandHandler("about", about_callback))
    application.add_handler(CommandHandler("help", help_callback))
    application.add_handler(CommandHandler("reset", reset_callback))
    application.add_handler(MessageHandler(filters.PHOTO, photo_callback))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

    # Terminate program
    sys.exit(0)


# Main program execution
if __name__ == "__main__":
    main()
