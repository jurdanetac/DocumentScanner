#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Import needed third-party libraries
# See requirements.txt for more information
import cv2
import logging
import numpy
import os
import Scanner
import sys
from io import BytesIO, StringIO
from pathlib import Path
from PIL import Image
from telegram import (
    constants,
    ForceReply,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


# Path of project directory root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Path of images directory
IMG_DIR = f"{ROOT_DIR}/images"
Path(IMG_DIR).mkdir(exist_ok=True)
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


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("TODO")


async def photo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to photos"""
    img = await context.bot.get_file(update.message.photo[-1])
    await img.download_to_drive(custom_path=f"{IMG_DIR}/{img.file_id}")
    await update.message.reply_text("I received your image. Metadata:")
    await update.message.reply_text(img)
    scanned_img = Scanner.scan(f"{IMG_DIR}/{img.file_id}")
    scanned_file = Image.fromarray(scanned_img)
    scanned_file_path = f"{IMG_DIR}/scanned_{img.file_id}.jpeg"
    scanned_file.save(scanned_file_path)
    await context.bot.send_document(
        chat_id=update.message["chat"]["id"],
        document=open(scanned_file_path, "rb"),
        filename=scanned_file_path,
    )


PHOTOS = range(1)


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!", reply_markup=ForceReply(selective=True)
    )

    return PHOTOS


async def photos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # reply_keyboard = [["Yes", "No"]]
    # photos = int(update.message.text)
    # logger.info("Page count of %s: %s", update.effective_user.first_name, str(photos))
    pass


def main() -> None:
    """Start the bot."""

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("about", about_callback))
    application.add_handler(CommandHandler("help", help_callback))
    application.add_handler(MessageHandler(filters.PHOTO, photo_callback))

    # Add conversation handler with the state PHOTOS
    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start", start_callback)],
    #     states={
    #         PHOTOS: [
    #             MessageHandler(filters.Regex("^[1-9]\d*$"), photos_callback),
    #         ],
    #     },
    #     fallbacks=[CommandHandler("cancel", cancel_callback)],
    # )

    # application.add_handler(conv_handler)

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

    # Terminate program
    sys.exit(0)


# Main program execution
if __name__ == "__main__":
    main()
