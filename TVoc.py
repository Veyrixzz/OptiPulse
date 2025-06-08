# meta developer: @OptiPulseMod
from .. import loader, utils
from telethon.tl.types import InputMediaUploadedDocument
import torch
import torchaudio
import os
import numpy as np
from pydub import AudioSegment

class TVocRealMod(loader.Module):
    strings = {"name": "TVocReal"}

    async def tvoccmd(self, message):
        """Озвучка текста красивым голосом. Использование: .tvoc <текст>"""
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("💬 Введи текст для озвучивания.")
            return

        await message.edit("🎧 Генерация голоса...")

        
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                  model='silero_tts',
                                  language='ru',
                                  speaker='kseniya')

        sample_rate = 48000
        speaker = 'kseniya'

        audio = model.apply_tts(text=text,
                                speaker=speaker,
                                sample_rate=sample_rate)

        wav_path = "/tmp/audio.wav"
        ogg_path = "/tmp/audio.ogg"

        torchaudio.save(wav_path, torch.tensor([audio]), sample_rate=sample_rate)

  
        sound = AudioSegment.from_wav(wav_path)
        sound.export(ogg_path, format="ogg", codec="libopus")

        await message.client.send_file(
            message.chat_id,
            ogg_path,
            voice_note=True,
            reply_to=message.reply_to_msg_id
        )
        await message.delete()

        os.remove(wav_path)
        os.remove(ogg_path)
