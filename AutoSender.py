# meta developer: @OptiPulseMod

"""
AutoSpammer Module for Heroku Userbot

Copyright (c) 2025 @OptiPulseMod


License:

EN:
This module is developed by @OptiPulseMod and provided "as is".
Use is only permitted in its original, unmodified form.
Copying, modification, or redistribution is strictly prohibited.

RU:
Этот модуль разработан @OptiPulseMod и предоставляется "как есть".
Использование разрешено только в оригинальном, неизменённом виде.
Копирование, модификация или распространение строго запрещены.
"""

from hikka import loader, utils
import asyncio
from telethon.tl.types import Dialog, Folder, InputPeerChannel, InputPeerChat

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
        "folder_processing": "📂 Обработка папки: {}",
        "folder_error": "❌ Ошибка при обработке папки: {}",
        "invalid_target": "❌ Некорректная цель: {}",
    }

    def __init__(self):
        self.text = None
        self.groups = []
        self.interval = 60
        self.task = None
        self.running = False
        self.message = None

    async def client_ready(self, client, db):
        self.client = client

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
        self.message = message
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

    async def _get_chats_from_folder(self, folder_name):
        """Получает все чаты из указанной папки"""
        try:
            dialogs = await self.client.get_dialogs()
            folder_chats = []
            
            for dialog in dialogs:
                if hasattr(dialog, 'folder') and dialog.folder and dialog.folder.title.lower() == folder_name.lower():
                    if isinstance(dialog.entity, (InputPeerChannel, InputPeerChat)):
                        folder_chats.append(dialog.entity)
                    else:
                        try:
                            entity = await self.client.get_input_entity(dialog.entity)
                            folder_chats.append(entity)
                        except Exception as e:
                            print(f"[AutoSpammer] Не удалось получить entity для диалога: {e}")
            
            return folder_chats
        except Exception as e:
            print(f"[AutoSpammer] Ошибка при получении чатов из папки: {e}")
            return []

    async def _autospam(self):
        while self.running:
            for target in self.groups:
                try:
                    # Если цель - папка (начинается с folder:)
                    if target.lower().startswith("folder:"):
                        folder_name = target[7:].strip()
                        await utils.answer(self.message, self.strings("folder_processing").format(folder_name))
                        
                        chats = await self._get_chats_from_folder(folder_name)
                        if not chats:
                            await utils.answer(self.message, self.strings("folder_error").format(folder_name))
                            continue
                            
                        for chat in chats:
                            try:
                                await self.client.send_message(chat, self.text)
                                await asyncio.sleep(1)  # Небольшая задержка между сообщениями
                            except Exception as e:
                                print(f"[AutoSpammer] Ошибка при отправке в чат {chat}: {e}")
                    else:
                        # Обычная группа/чат
                        try:
                            await self.client.send_message(target, self.text)
                        except Exception as e:
                            print(f"[AutoSpammer] Ошибка при отправке в {target}: {e}")
                            await utils.answer(self.message, self.strings("invalid_target").format(target))
                except Exception as e:
                    print(f"[AutoSpammer] Ошибка при обработке цели {target}: {e}")
            
            await asyncio.sleep(self.interval)
