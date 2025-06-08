# meta developer: @OptiPulseMod



from .. import loader, utils
import edge_tts
import asyncio
import os
from tempfile import NamedTemporaryFile

@loader.tds
class TVocEdge(loader.Module):
    """Озвучка текста."""
    strings = {
        "name": "TVoc",
        "no_text": "❌ Укажи текст для озвучки.",
        "error": "❌ Ошибка TTS: ",
        "voices": "🎤 Примеры голосов:\n- ru-RU-SvetlanaNeural (женский)\n- ru-RU-DmitryNeural (мужской)",
        "setvoice": "✅ Голос установлен: ",
    }

    def __init__(self):
        self.voice = "ru-RU-SvetlanaNeural"

    async def tvoccmd(self, message):
        """Озвучить текст: .tvoc <текст>"""
        text = utils.get_args_raw(message)
        if not text:
            return await utils.answer(message, self.strings("no_text"))

        path = None
        try:
            with NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                path = f.name

            communicate = edge_tts.Communicate(text=text, voice=self.voice)
            await communicate.save(path)

            await message.client.send_file(
                message.chat_id,
                file=path,
                voice_note=True,
                reply_to=message.reply_to_msg_id
            )
        except Exception as e:
            return await utils.answer(message, self.strings("error") + str(e))
        finally:
            if path and os.path.exists(path):
                os.remove(path)
            await message.delete()

    async def tvocvoicecmd(self, message):
        """Изменить голос: .tvocvoice <имя>"""
        voice = utils.get_args_raw(message).strip()
        if voice:
            self.voice = voice
            await utils.answer(message, self.strings("setvoice") + voice)
        else:
            await utils.answer(message, self.strings("voices"))

    async def tvocvoicescmd(self, message):
        """Показать примеры голосов: .tvocvoices"""
        await utils.answer(message, self.strings("voices"))
