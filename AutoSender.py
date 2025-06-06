
# meta developer: @OptiPulseMod


"""
AutoSpammer Module for Hikka Userbot

Copyright (c) 2025 @OptiPulseMod


License:

EN:
This module is developed by @veyrixzz and provided "as is".
Use is only permitted in its original, unmodified form.
Copying, modification, or redistribution is strictly prohibited.

RU:
Этот модуль разработан @OptiPulseMod и предоставляется "как есть".
Использование разрешено только в оригинальном, неизменённом виде.
Копирование, модификация или распространение строго запрещены.
"""
from hikka import loader, utils
import asyncio

@loader.tds
class AutoSenderMod(loader.Module):
    strings = {
        "name": "AutoSpammer",
        "startspam": "✅ Авторассылка запущена.",
        "stopspam": "⛔ Авторассылка остановлена.",
        "intervalset": "⏱ Интервал установлен: {} секунд.",
        "textset": "📝 Текст сообщения установлен.",
        "groupsset": "📨 Группы установлены: {}.",
        "nogroups": "❌ Не указаны группы.",
        "notext": "❌ Не указан текст сообщения.",
    }

    def __init__(self):
        self.text = None
        self.groups = []
        self.interval = 60
        self.task = None
        self.running = False

    async def autogroupcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_groups"))
        self.groups = args.split()
        await utils.answer(message, self.strings("groups_set").format(', '.join(self.groups)))

    async def autotextcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_text"))
        self.text = args
        await utils.answer(message, self.strings("text_set"))

    async def autotimecmd(self, message):
        args = utils.get_args(message)
        if not args or not args[0].isdigit():
            return await utils.answer(message, "❌ Укажите корректное число в секундах.")
        self.interval = int(args[0])
        await utils.answer(message, self.strings("interval_set").format(self.interval))

    async def autosendcmd(self, message):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            return await utils.answer(message, self.strings("stop_spam"))
        if not self.groups:
            return await utils.answer(message, self.strings("no_groups"))
        if not self.text:
            return await utils.answer(message, self.strings("no_text"))

        self.running = True
        self.task = asyncio.create_task(self._autospam())
        await utils.answer(message, self.strings("start_spam"))

    async def _autospam(self):
        try:
            while self.running:
                for group in self.groups:
                    try:
                        await self._client.send_message(group, self.text)
                    except Exception as e:
                        print(f"[AutoSpammer] Не удалось отправить сообщение в {group}: {e}")
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass
