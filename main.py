from telegram.constants import ChatAction
import os
from telegram import Update, InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests
from bs4 import BeautifulSoup
import json
from pytube import YouTube
from email.message import EmailMessage
import smtplib
import ssl

tg_api = "6669667485:AAGCeiXJ7HHQc5p-slpFInoWyCQIFP-ZMMA"
api_key = 'AIzaSyCfIyM5ZyB4hoKAzIRq8elN-_ZdXoCp5G8'
public_api = "AIzaSyCfIyM5ZyB4hoKAzIRq8elN-_ZdXoCp5G8"

TOKEN = "6669667485:AAGCeiXJ7HHQc5p-slpFInoWyCQIFP-ZMMA"
BOT_USERNAME = "@ordi_musicBot"


def send_email(body):
    sender = 'tunar3950@gmail.com'
    psw = 'dcijbiwfmwtrmvnn'
    receiver = 'tunar.memmedov@icloud.com'
    subject = f'OrdiMUS BOT'
    body = body

    em = EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender, psw)
        smtp.send_message(em)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    us_id = update.message.chat_id
    await update.message.reply_text(
        f"Hello {user}! I am OrdiMus. I can install music or YouTube video for you.\n If you want to install music just type music name,\n If you want to install YouTube video send YouTube link. :)")

    send_email(f'User:{user}\nID:{us_id} sent "/start"')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    us_id = update.message.chat_id
    await update.message.reply_text(
        "Type music name to download or send a YouTube video link to download.\nStill need help?\nContact @tunbyte for help.")

    send_email(f'User:{user}\nID:{us_id} sent "/help"')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.first_name
    us_id = update.message.chat_id
    global song_name
    song_name = update.message.text
    try:

        if "https://" in song_name:
            link = YouTube(song_name)
            song = link.streams.get_highest_resolution().download(filename=f"{link.title}")

            try:
                await update.message.reply_chat_action(action=ChatAction.UPLOAD_VIDEO)
                with open(song, "rb") as file:
                    await update.message.reply_video(video=file, duration=link.length, supports_streaming=True, caption=f"{BOT_USERNAME}")
                await update.message.reply_text("Downloaded succesfully")
                os.remove(song)
            except Exception as e:
                await update.message.reply_text(f"{e}")
        else:
            url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={song_name}&key={public_api}"
            r = requests.get(url).text
            soup = BeautifulSoup(r, 'html.parser')

            a = str(soup)
            b = json.loads(a)

            keyboard = []
            try:
                for item in b['items']:
                    if 'videoId' in item.get('id', {}):
                        video_id = item['id']['videoId']
                        video_title = item['snippet']['title']
                        keyboard.append([InlineKeyboardButton(video_title, callback_data=video_id)])
            except Exception as e:
                await update.message.reply_text(f"An error occurred: {e}\nPlease send this error message to @tunbyte.")

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text("Please choose a song:", reply_markup=reply_markup)



    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}\nPlease send this error message to @tunbyte.")

    send_email(f'User:{user}\nID:{us_id}\nMessage: {song_name}')


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.message.from_user.first_name
    chat_id = query.message.chat_id
    try:
        await query.answer()
        video_url = "https://www.youtube.com/watch?v=" + query.data
        yt = YouTube(video_url)
        song = yt.streams.filter(only_audio=True).first()
        file = song.download(filename=f"{yt.title}")

        await query.message.reply_text("Downloading...")
        await query.message.reply_chat_action(action=ChatAction.UPLOAD_VOICE)
        try:
            with open(file, "rb") as file:
                await query.message.reply_audio(audio=file, duration=yt.length, caption=f"{BOT_USERNAME}")
            await query.message.reply_text("Downloaded successfully")
            os.remove(file.name)
        except Exception as e:
            await query.message.reply_text(f"An error occurred: {e}\nPlease send this error message to @tunbyte.")
    except Exception as e:
        await query.message.reply_text(f"An error occurred: {e}\nPlease send this error message to @tunbyte.")

# async def va(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     try:
#         await query.answer()

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print("BOT starting...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    app.add_handler(CallbackQueryHandler(button))
    # app.add_handler(CallbackQueryHandler(va))

    app.add_handler(MessageHandler(filters.AUDIO, handle_message))
    app.add_handler(MessageHandler(filters.VIDEO, handle_message))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print("BOT polling...")
    app.run_polling(poll_interval=1.0)