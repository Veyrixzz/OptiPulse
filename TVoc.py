# meta developer: @OptiPulseMod

from .. import loader, utils
from pydub import AudioSegment
import requests, os

class TVoc(loader.Module):
    strings = {"name": "TVoc"}

    async def client_ready(self, client, db):
        self.db = db
        self.voice = db.get("TVoc", "voice", "Olga")
        self.key = os.getenv("0ef1358805f24629a3ee6b87f3414f26")

    async def tvoccmd(self, message):
        """Озвучивает текст голосом — .tvoc <текст>"""
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("💬 Использование: `.tvoc Привет, мир!`")
            return
        if not self.key:
            await message.edit("❌ VoiceRSS API-ключ не найден. Установи переменную окружения `VOICERSS_API_KEY`.")
            return

        await message.edit(f"🎤 Генерация речи (голос: {self.voice})...")

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
                await message.edit("❌ Ошибка генерации речи. Проверь API-ключ и параметры.")
                return
            mp3 = "/tmp/tvoc.mp3"
            ogg = "/tmp/tvoc.ogg"
            with open(mp3, "wb") as f: f.write(r.content)
            AudioSegment.from_mp3(mp3).export(ogg, format="ogg", codec="libopus")
            await message.client.send_file(message.chat_id, ogg, voice_note=True,
                                           reply_to=message.reply_to_msg_id)
            await message.delete()
            os.remove(mp3)
            os.remove(ogg)
        except Exception as e:
            await message.edit(f"❌ Ошибка: {e}")

    async def setvoicecmd(self, message):
        """Меняет голос — .setvoice <имя>"""
        name = utils.get_args_raw(message).strip()
        avail = ["Olga", "Marina"]
        if not name:
            await message.edit(f"🎙 Текущий голос: {self.voice}\nДоступные голоса: {', '.join(avail)}")
            return
        if name not in avail:
            await message.edit(f"❌ Голос не найден. Доступные: {', '.join(avail)}")
            return
        self.db.set("TVoc", "voice", name)
        self.voice = name
        await message.edit(f"✅ Установлен голос: {name}")

    async def voicescmd(self, message):
        """Показывает список доступных голосов — .voices"""
        await message.edit("🎧 Доступные голоса:\n- Olga (женский, стандарт)\n- Marina (женский, нейтральный)\nСменить голос: `.setvoice <имя>`")
