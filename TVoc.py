# meta developer: @OptiPulseMod

from .. import loader, utils
from pydub import AudioSegment
import requests
import os

class TVoc(loader.Module):
    strings = {"name": "TVoc"}

    async def client_ready(self, client, db):
        self.db = db
        self.voice = self.db.get("TVoc", "voice", "kseniya")

    async def tvoccmd(self, message):
        """Озвучивает текст голосом. Использование: .tvoc <текст>"""
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("💬 Введи текст для озвучивания.")
            return

        await message.edit(f"🎤 Генерация... (голос: {self.voice})")

        tts_url = "https://api.v6.anon-tts.ru/generate"

        payload = {
            "text": text,
            "voice": self.voice,
            "lang": "ru"
        }

        try:
            response = requests.post(tts_url, json=payload, timeout=30)
            if response.status_code != 200 or "url" not in response.json():
                await message.edit("❌ Ошибка генерации речи.")
                return

            audio_url = response.json()["url"]
            audio_data = requests.get(audio_url)

            mp3_path = "/tmp/tvoc.mp3"
            ogg_path = "/tmp/tvoc.ogg"

            with open(mp3_path, "wb") as f:
                f.write(audio_data.content)

            sound = AudioSegment.from_mp3(mp3_path)
            sound.export(ogg_path, format="ogg", codec="libopus")

            await message.client.send_file(
                message.chat_id,
                ogg_path,
                voice_note=True,
                reply_to=message.reply_to_msg_id
            )
            await message.delete()

            os.remove(mp3_path)
            os.remove(ogg_path)

        except Exception as e:
            await message.edit(f"❌ Ошибка: {e}")

    async def setvoicecmd(self, message):
        """Установить голос. Пример: .setvoice kseniya"""
        args = utils.get_args_raw(message).strip()
        valid_voices = ["kseniya", "xenia", "baya", "aidar", "zahar", "jane", "oksana", "alyss"]

        if not args:
            await message.edit(f"🎙 Текущий голос: {self.voice}\nДоступные: {', '.join(valid_voices)}")
            return

        if args not in valid_voices:
            await message.edit(f"❌ Голос не найден. Доступные: {', '.join(valid_voices)}")
            return

        self.db.set("TVoc", "voice", args)
        self.voice = args
        await message.edit(f"✅ Голос установлен: {args}")
