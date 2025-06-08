# meta developer: @OptiPulseMod




from .. import loader, utils
from gtts import gTTS
from pydub import AudioSegment
import os
import io

class TVoc(loader.Module):
    strings = {"name": "TVoc"}

    async def client_ready(self, client, db):
        self.voice = self.get("voice", "ru")  # ru = женский русский

    async def tvoccmd(self, message):
        text = utils.get_args_raw(message)
        if not text:
            return await message.edit("💬 Введите текст: `.tvoc Привет, мир!`")

        await message.edit(f"🎤 Генерирую речь ({self.voice})...")
        try:
            tts = gTTS(text=text, lang=self.voice)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            ogg_fp = io.BytesIO()
            sound = AudioSegment.from_file(mp3_fp, format="mp3")
            sound.export(ogg_fp, format="ogg", codec="libopus")
            ogg_fp.seek(0)

            await message.client.send_file(message.chat_id, ogg_fp, voice_note=True,
                                           reply_to=message.reply_to_msg_id)
            await message.delete()
        except Exception as e:
            await message.edit(f"❌ Ошибка TTS: {e}")

    async def setvoicecmd(self, message):
        name = utils.get_args_raw(message).strip()
        avail = {"ru": "женский русский", "ru-fast": "русский, быстрее"}
        if not name:
            return await message.edit(f"🎙 Текущий голос: {self.voice}\nДоступны: {', '.join(avail.keys())}")

        if name not in avail:
            return await message.edit(f"❌ Нет такого голоса. Доступны: {', '.join(avail.keys())}")

        self.set("voice", name)
        self.voice = name
        await message.edit(f"✅ Голос установлен: {name} ({avail[name]})")

    async def voicescmd(self, message):
        await message.edit("🎧 Доступные голоса:\n- ru (русский, женский)\n- ru-fast (русский, под быструю речь)\nСменить: `.setvoice <имя>`")
