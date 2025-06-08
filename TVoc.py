# meta developer: @OptiPulseMod


from .. import loader, utils
import requests, os
from pydub import AudioSegment

class TVoc(loader.Module):
    strings = {"name": "TVoc"}

    async def client_ready(self, client, db):
        self.voice = self.get("voice", "Olga")
        self.key = "ВОТ_ТУТ_ТВОЙ_VOICERSS_API_KEY"

    async def tvoccmd(self, message):
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("Введи текст после .tvoc")
            return

        await message.edit(f"🎤 Генерация речи ({self.voice})…")
        try:
            params = {
                "key": self.key,
                "hl": "ru-ru",
                "v": self.voice,
                "r": "0",
                "c": "MP3",
                "f": "8khz_8bit_mono",
                "src": text
            }
            r = requests.get("https://api.voicerss.org/", params=params, timeout=30)
            if r.status_code != 200 or r.content.startswith(b"ERROR"):
                await message.edit("Ошибка генерации речи.")
                return
            mp3 = "/tmp/tvoc.mp3"
            ogg = "/tmp/tvoc.ogg"
            with open(mp3, "wb") as f: f.write(r.content)
            AudioSegment.from_mp3(mp3).export(ogg, format="ogg", codec="libopus")
            await message.client.send_file(message.chat_id, ogg, voice_note=True, reply_to=message.reply_to_msg_id)
            await message.delete()
            os.remove(mp3)
            os.remove(ogg)
        except Exception as e:
            await message.edit(f"Ошибка: {e}")

    async def setvoicecmd(self, message):
        name = utils.get_args_raw(message).strip()
        avail = ["Olga", "Marina", "Tatyana", "Irina"]
        if not name:
            await message.edit(f"Текущий голос: {self.voice}\nДоступные: {', '.join(avail)}")
            return
        if name not in avail:
            await message.edit(f"Нет такого голоса. Доступные: {', '.join(avail)}")
            return
        self.set("voice", name)
        self.voice = name
        await message.edit(f"Голос установлен: {name}")

    async def voicescmd(self, message):
        await message.edit("Голоса:\n- Olga\n- Marina\n- Tatyana\n- Irina\nСменить: .setvoice <имя>")
