
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
    """Авторассылка сообщений в выбранные группы/папки через заданный интервал"""

    strings = {
        "name": "AutoSpammer",
        "start_spam": "✅ Авторассылка запущена.",
        "stop_spam": "⛔ Авторассылка остановлена.",
        "interval_set": "⏱ Интервал установлен: {} секунд.",
        "text_set": "📝 Текст сообщения установлен.",
        "groups_set": "📨 Группы/папки установлены: {}.",
        "no_groups": "❌ Не указаны группы/папки.",
        "no_text": "❌ Не указан текст сообщения.",
    }

    def __init__(self):
        self.text = None
        self.groups = []
        self.interval = 60
        self.task = None
        self.running = False

    async def autogroupcmd(self, message):
        """<ссылки_или_ID_групп/папок> — Установить список групп/папок для авторассылки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_groups"))
        self.groups = args.split()
        await utils.answer(message, self.strings("groups_set").format(', '.join(self.groups)))

    async def autotextcmd(self, message):
        """<текст> — Установить текст для авторассылки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_text"))
        self.text = args
        await utils.answer(message, self.strings("text_set"))

    async def autotimecmd(self, message):
        """<секунды> — Установить интервал между сообщениями"""
        args = utils.get_args(message)
        if not args or not args[0].isdigit():
            return await utils.answer(message, "❌ Укажите корректное число в секундах.")
        self.interval = int(args[0])
        await utils.answer(message, self.strings("interval_set").format(self.interval))

    async def autosendcmd(self, message):
        """Включить или выключить авторассылку"""
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

    async def _get_chats_from_folder(self, folder_link):
        """Получает все чаты из указанной папки"""
        try:
            folder = await self._client.get_entity(folder_link)
            if not hasattr(folder, 'chats'):
                return []
            return folder.chats
        except Exception as e:
            print(f"[AutoSpammer] Ошибка при получении чатов из папки: {e}")
            return []

    async def _autospam(self):
        try:
            while self.running:
                for target in self.groups:
                    try:
                        if "folder" in target.lower():
                            chats = await self._get_chats_from_folder(target)
                            for chat in chats:
                                try:
                                    await self._client.send_message(chat.id, self.text)
                                except Exception as e:
                                    print(f"[AutoSpammer] Не удалось отправить сообщение в чат {chat.id} из папки: {e}")
                        else:
                            await self._client.send_message(target, self.text)
                    except Exception as e:
                        print(f"[AutoSpammer] Ошибка при обработке цели {target}: {e}")
                
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            pass
