#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importar libreriías necesarias
# Véase requirements.txt para más información

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

# Ruta del directorio origen
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ruta de los directorios de las imágenes
IMG_DIR = f"{ROOT_DIR}/images"
SCANNED_IMG_DIR = f"{ROOT_DIR}/images/scanned"
ORIGINAL_IMG_DIR = f"{ROOT_DIR}/images/original"
# Ruta del directorio de los documentos pdf
PDF_DIR = f"{ROOT_DIR}/pdf"
# Ruta del token del bot
TOKEN_PATH = f"{ROOT_DIR}/token"

last_sent_pic = {}


# Leer token
try:
    with open(TOKEN_PATH, mode="r", encoding="utf-8") as file:
        TOKEN = file.read().strip()
except FileNotFoundError:
    print("No se encontró el token del bot")
    sys.exit(1)


# Imprimir operaciones a la consola
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responder al enviar el comando /about"""
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
    """Eliminar imágenes enviadas anteriormente"""
    shutil.rmtree(f"{ORIGINAL_IMG_DIR}/{user}", ignore_errors=True)
    shutil.rmtree(f"{SCANNED_IMG_DIR}/{user}", ignore_errors=True)
    shutil.rmtree(f"{PDF_DIR}/{user}", ignore_errors=True)
    Path(f"{ORIGINAL_IMG_DIR}/{user}").mkdir(exist_ok=True)
    Path(f"{SCANNED_IMG_DIR}/{user}").mkdir(exist_ok=True)
    Path(f"{PDF_DIR}/{user}").mkdir(exist_ok=True)
    last_sent_pic[user] = []


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responder al enviar el comando /start"""
    Path(IMG_DIR).mkdir(exist_ok=True)
    Path(SCANNED_IMG_DIR).mkdir(exist_ok=True)
    Path(ORIGINAL_IMG_DIR).mkdir(exist_ok=True)

    user = str(update["message"]["chat"]["id"])
    reset_chat(user)
    last_sent_pic[user] = []

    await update.message.reply_html(rf"Hola {update.effective_user.mention_html()}!")
    await update.message.reply_html(
        r"Envíame una foto del documento! 📸📄",
        reply_markup=ForceReply(selective=True),
    )


async def reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Eliminar imágenes enviadas cuando se envía el comando /reset"""
    user = str(update["message"]["chat"]["id"])
    reset_chat(user)
    await update.message.reply_html("Reseteo completado exitosamente")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responder al enviar el comando /help"""
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
    """Responder a imagenes"""
    user = str(update["message"]["chat"]["id"])

    await update.message.reply_text(
        "*Procesando\.\.\.*",
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
            "*Asegúrese de que los bordes de la hoja son distinguibles de la superficie\!*",
            parse_mode=constants.ParseMode.MARKDOWN_V2,
        )
        return

    if user not in last_sent_pic:
        last_sent_pic[user] = []

    last_sent_pic[user].append(f"{img.file_id}.jpeg")
    scanned_file = Image.fromarray(scanned_img)
    scanned_file_path = f"{SCANNED_IMG_DIR}/{user}/scanned_{img.file_id}.jpeg"
    scanned_file.save(scanned_file_path)

    await update.message.reply_text(
        "Imagen escaneada\. Para descartarla del documento utilice`/last`",
        parse_mode=constants.ParseMode.MARKDOWN_V2,
    )

    with open(scanned_file_path, "rb") as doc:
        await context.bot.send_document(
            chat_id=update.message["chat"]["id"],
            document=doc,
            filename=scanned_file_path,
        )


async def last_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Descartar última imagen enviada"""
    user = str(update.message["chat"]["id"])
    if user in last_sent_pic and last_sent_pic[user]:
        try:
            os.remove(f"{SCANNED_IMG_DIR}/{user}/scanned_{last_sent_pic[user][-1]}")
            os.remove(f"{ORIGINAL_IMG_DIR}/{user}/{last_sent_pic[user][-1]}")
            last_sent_pic[user].pop()
            await update.message.reply_html("Imagen descartada.")
        except OSError as os_error:
            print(os_error)
            await update.message.reply_html("No hay más imágenes.")
    else:
        await update.message.reply_html("No ha enviado ninguna imagen aún.")


async def pdf_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convertir a pdf las imágenes y reenviar al usuario"""
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
        with open(pdf_path, mode="rb") as doc:
            await context.bot.send_document(
                chat_id=update.message["chat"]["id"],
                document=doc,
                filename=pdf_name,
            )
    else:
        await update.message.reply_html("Debes escanear 1 documento al menos!")


def main() -> None:
    """Iniciar el bot."""

    # Crear aplicación y pasarle el token como argumento
    application = ApplicationBuilder().token(TOKEN).build()

    # Responder comandos en Telegram
    application.add_handler(CommandHandler("about", about_callback))
    application.add_handler(CommandHandler("help", help_callback))
    application.add_handler(CommandHandler("last", last_callback))
    application.add_handler(CommandHandler("pdf", pdf_callback))
    application.add_handler(CommandHandler("reset", reset_callback))
    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(MessageHandler(filters.PHOTO, photo_callback))

    # Ejecutar bot hasta que el usuario presione Ctrl-C
    application.run_polling()

    # Terminar programa
    sys.exit(0)


# Ejecución principal
if __name__ == "__main__":
    main()
