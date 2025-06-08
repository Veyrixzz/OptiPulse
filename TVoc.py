# meta developer: @OptiPulseMod

from .. import loader, utils
from pydub import AudioSegment
import requests, os

class TVoc(loader.Module):
    strings = {"name": "TVoc"}

    async def client_ready(self, client, db):
        self.db = db
        self.voice = db.get("TVoc", "voice", "Olga")
        self.key = os.getenv("VOICERSS_API_KEY")
        if not self.key:
            client.logger.error("TVoc: отсутствует VOICERSS_API_KEY")

    async def tvoccmd(self, message):
        """.tvoc <текст> — озвучить текст текущим голосом."""
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("💬 Использование: `.tvoc Привет, мир!`")
            return
        if not self.key:
            await message.edit("❌ Ошибка: нужен VoiceRSS API‑ключ. Установи VOICERSS_API_KEY.")
            return

        await message.edit(f"🎤 Генерация (голос: {self.voice})…")

        params = {
            "key": self.key,
            "hl": "ru-ru",
            "v": self.voice,
            "r": "0",
            "c": "MP3",
            "f": "8khz_8bit_mono",
            "src": text
        }
        try:
            r = requests.get("https://api.voicerss.org/", params=params, timeout=30)
            if r.status_code != 200 or r.content.startswith(b"ERROR"):
                await message.edit("❌ Ошибка генерации речи.")
                return
            mp3 = "/tmp/tvoc.mp3"
            ogg = "/tmp/tvoc.ogg"
            with open(mp3, "wb") as f: f.write(r.content)
            AudioSegment.from_mp3(mp3).export(ogg, format="ogg", codec="libopus")
            await message.client.send_file(message.chat_id, ogg, voice_note=True,
                                           reply_to=message.reply_to_msg_id)
            await message.delete()
            os.remove(mp3); os.remove(ogg)
        except Exception as e:
            await message.edit(f"❌ Ошибка: {e}")

    async def setvoicecmd(self, message):
        """.setvoice <имя> — выбрать голос (например, Olga или Marina)."""
        name = utils.get_args_raw(message).strip()
        avail = ["Olga", "Marina"]
        if not name:
            await message.edit(f"ℹ️ Текущий голос: {self.voice}\nДоступные голоса: {', '.join(avail)}\nИспользование: `.setvoice Olga`")
            return
        if name not in avail:
            await message.edit(f"❌ Голос не найден. Доступны: {', '.join(avail)}")
            return
        self.db.set("TVoc", "voice", name)
        self.voice = name
        await message.edit(f"✅ Голос установлен: {name}")

    async def voicescmd(self, message):
        """.voices — показать список доступных голосов."""
        await message.edit("🎙 Используемые голоса: Olga (женский стандарт), Marina (нейтральный женский)\nСменить голос: `.setvoice <имя>`")
