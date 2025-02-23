import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL

# API və Bot məlumatları
API_ID = 10708442
API_HASH = "05596a543eff3160508b49518111660c"
BOT_TOKEN = "8190547317:AAHaFYXNdpU8lBGBdGHX80QrsMCy4TkFoQI"

# Pyrogram və PyTgCalls yaradılması
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

# Youtube axtarışı üçün funksiya
def search_youtube(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "default_search": "ytsearch",
        "quiet": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        return info["entries"][0]["url"] if "entries" in info else info["url"]

# Youtube audio yükləmə funksiyası
def download_audio(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"downloads/{info['id']}.mp3"

# Qrup üzvü dəyişdikdə mesaj göndərilməsi
@app.on_chat_member_updated
async def on_member_updated(_, chat_member):
    if chat_member.new_chat_member.status in ("administrator", "creator"):
        chat_id = chat_member.chat.id
        await app.send_message(chat_id, "Salam! Mən artıq bu qrupda musiqi botu kimi fəaliyyət göstərə bilərəm. 🎵")

# "play" əmri ilə musiqi çalma
@app.on_message(filters.command("play") & filters.group)
def play(_, message):
    if len(message.command) < 2:
        message.reply_text("Zəhmət olmasa musiqinin adını və ya linkini əlavə edin!")
        return
    query = " ".join(message.command[1:])
    url = search_youtube(query)
    file_path = download_audio(url)
    chat_id = message.chat.id
    call.join_group_call(chat_id, AudioPiped(file_path))
    message.reply_text(f"Musiqi çalınır: {query}")

# "pause" əmri ilə musiqini dayandırma
@app.on_message(filters.command("pause") & filters.group)
def pause(_, message):
    call.pause_stream(message.chat.id)
    message.reply_text("Musiqi dayandırıldı ⏸️")

# "resume" əmri ilə musiqini davam etdirmə
@app.on_message(filters.command("resume") & filters.group)
def resume(_, message):
    call.resume_stream(message.chat.id)
    message.reply_text("Musiqi davam etdirildi ▶️")

# "skip" əmri ilə musiqini keçirmək
@app.on_message(filters.command("skip") & filters.group)
def skip(_, message):
    call.stop()
    message.reply_text("Cari musiqi ötürüldü ⏭️")

# "stop" əmri ilə musiqini dayandırıb, səs kanalından çıxmaq
@app.on_message(filters.command("stop") & filters.group)
def stop(_, message):
    chat_id = message.chat.id
    call.leave_group_call(chat_id)
    message.reply_text("Musiqi dayandırıldı və bot səs kanalından çıxdı ⏹️")

# Botu işə salmaq
app.run()