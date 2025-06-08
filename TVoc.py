# meta developer: @OptiPulseMod

from .. import loader, utils
from pydub import AudioSegment
import requests
import os

class TVoc(loader.Module):
    strings = {"name": "TVoc"}

    async def tvoccmd(self, message):
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("💬 Введи текст для озвучивания.")
            return

        await message.edit("🔊 Генерация аудио...")

        tts_url = "https://api.tts.land/v1/tts"
        payload = {"text": text, "voice": "kseniya", "lang": "ru"}

        try:
            response = requests.post(tts_url, json=payload)
            if response.status_code != 200 or "audio" not in response.json():
                await message.edit("❌ Ошибка генерации речи.")
                return

            audio_url = response.json()["audio"]
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
