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

from PIL import Image
from telegram import (
    ForceReply,
    Update,
    constants,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
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

last_sent_pic = {}


# Load bot token
try:
    with open(TOKEN_PATH, mode="r", encoding="utf-8") as file:
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
        "Proyecto final\.\n"
        "_Programación III N\-612 2023\._\n\n"
        "*__Integrantes__\:*\n"
        "\- Baez, Samuel\n"
        "\- Mavares, Cesar \n"
        "\- Urdaneta, Juan\n\n"
        "https\:\/\/github\.com\/jurdanetac\/DocumentScanner",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )


def reset_chat(user: str) -> None:
    """Delete previously sent pictures"""
    shutil.rmtree(f"{ORIGINAL_IMG_DIR}/{user}", ignore_errors=True)
    shutil.rmtree(f"{SCANNED_IMG_DIR}/{user}", ignore_errors=True)
    shutil.rmtree(f"{PDF_DIR}/{user}", ignore_errors=True)
    Path(f"{ORIGINAL_IMG_DIR}/{user}").mkdir(exist_ok=True)
    Path(f"{SCANNED_IMG_DIR}/{user}").mkdir(exist_ok=True)
    Path(f"{PDF_DIR}/{user}").mkdir(exist_ok=True)
    last_sent_pic[user] = []


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    Path(IMG_DIR).mkdir(exist_ok=True)
    Path(SCANNED_IMG_DIR).mkdir(exist_ok=True)
    Path(ORIGINAL_IMG_DIR).mkdir(exist_ok=True)

    user = str(update["message"]["chat"]["id"])
    reset_chat(user)
    last_sent_pic[user] = []

    user = update.effective_user
    await update.message.reply_html(rf"Hi {user.mention_html()}!")
    await update.message.reply_html(
        r"Send me a photo of a document! 📸📄",
        reply_markup=ForceReply(selective=True),
    )


async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear old pictures stored when the command /reset is issued."""
    user = str(update["message"]["chat"]["id"])
    reset_chat(user)
    await update.message.reply_html("Reset performed successfully.")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "__*Comandos disponibles:*__\n\n"
        "`/start` \- Inicia las funciones del bot\. Luego de colocar este comando, envía las imágenes que deseas procesar\.\n\n"
        "`/pdf` \- Convertir las imágenes enviadas a formato pdf\. Es necesario inicializar las funciones y enviar las imágenes de antemano\. Las imágenes se verán mejoradas a la hora de la conversión\.\n\n"
        "`/reset` \- Limpia las imágenes colocadas anteriormente para inciar un nuevo documento pdf\. En caso de querer realizar un nuevo documento o reordenar las imágenes, utilice este comando\.\n\n"
        "`/last` \- Descartar la última foto enviada, si la hay\.\n\n"
        "`/help` \- Muestra los comandos disponibles\.",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )


async def photo_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Respond to photos"""
    user = str(update["message"]["chat"]["id"])

    await update.message.reply_text(
        "*Proccessing\.\.\.*",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )

    img = await context.bot.get_file(update.message.photo[-1])
    await img.download_to_drive(
        custom_path=f"{ORIGINAL_IMG_DIR}/{user}/{img.file_id}.jpeg"
    )

    try:
        scanned_img = Scanner.scan(f"{ORIGINAL_IMG_DIR}/{user}/{img.file_id}.jpeg")
    except cv2.error as cv_error:
        print(cv_error)
        await update.message.reply_text(
            "*Make sure the borders of the document are distinguishable from the surface\!*",
            parse_mode=constants.ParseMode.MARKDOWN_V2,
        )
        return

    last_sent_pic[user].append(f"{img.file_id}.jpeg")
    scanned_file = Image.fromarray(scanned_img)
    scanned_file_path = f"{SCANNED_IMG_DIR}/{user}/scanned_{img.file_id}.jpeg"
    scanned_file.save(scanned_file_path)

    await update.message.reply_text(
        "Image scanned\. To discard from document use `/last`",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )

    with open(scanned_file_path, "rb", enconding="utf-8") as doc:
        await context.bot.send_document(
            chat_id=update.message["chat"]["id"],
            document=doc,
            filename=scanned_file_path,
        )


async def last_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Discard last image sent"""
    user = str(update.message["chat"]["id"])
    if user in last_sent_pic and last_sent_pic[user]:
        try:
            os.remove(f"{SCANNED_IMG_DIR}/{user}/scanned_{last_sent_pic[user][-1]}")
            os.remove(f"{ORIGINAL_IMG_DIR}/{user}/{last_sent_pic[user][-1]}")
            last_sent_pic[user].pop()
            await update.message.reply_html("Image discarded.")
        except OSError as os_error:
            print(os_error)
            await update.message.reply_html("No images remaining.")
    else:
        await update.message.reply_html("You haven't sent an image yet.")


async def pdf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert to pdf sent images and send the document back to the user"""
    user = str(update["message"]["chat"]["id"])

    if os.listdir(f"{SCANNED_IMG_DIR}/{user}"):
        images = [
            Image.open(f"{SCANNED_IMG_DIR}/{user}/{f}")
            for f in os.listdir(f"{SCANNED_IMG_DIR}/{user}")
        ]
        pdf_name = time.strftime("%Y%m%d-%H%M%S") + ".pdf"
        pdf_path = f"{PDF_DIR}/{user}/{pdf_name}"
        images[0].save(
            pdf_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:],
        )
        with open(pdf_path, mode="rb", encoding="utf-8") as doc:
            await context.bot.send_document(
                chat_id=update.message["chat"]["id"],
                document=doc,
                filename=pdf_name,
            )
    else:
        await update.message.reply_html("You have to scan at least 1 document first!")


def main() -> None:
    """Start the bot."""

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("about", about_callback))
    application.add_handler(CommandHandler("help", help_callback))
    application.add_handler(CommandHandler("last", last_callback))
    application.add_handler(CommandHandler("pdf", pdf_callback))
    application.add_handler(CommandHandler("reset", reset_callback))
    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(MessageHandler(filters.PHOTO, photo_callback))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

    # Terminate program
    sys.exit(0)


# Main program execution
if __name__ == "__main__":
    main()
