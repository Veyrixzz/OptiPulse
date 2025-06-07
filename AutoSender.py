# meta developer: @OptiPulseMod

"""
AutoSpammer Module for Heroku Userbot

Copyright (c) 2025 @OptiPulseMod

License:
This module is developed by @OptiPulseMod and provided "as is".
Use is only permitted in its original, unmodified form.
Copying, modification, or redistribution is strictly prohibited.
"""

from hikka import loader, utils
import asyncio
from telethon.tl.types import Dialog, Folder, InputPeerChannel, InputPeerChat

@loader.tds
class AutoSenderMod(loader.Module):
    """Авторассылка в чаты/папки с раздельными настройками"""

    strings = {
        "name": "AutoSpammerPro",
        "start_spam": "✅ Авторассылка запущена.",
        "stop_spam": "⛔ Авторассылка остановлена.",
        "interval_set": "⏱ Интервал установлен: {} секунд.",
        "text_set": "📝 Текст сообщения установлен.",
        "chats_set": "💬 Чаты установлены: {}.",
        "folders_set": "📂 Папки установлены: {}.",
        "no_targets": "❌ Не указаны ни чаты, ни папки.",
        "no_text": "❌ Не указан текст сообщения.",
        "folder_processing": "📂 Обработка папки: {} ({} чатов)",
        "folder_error": "❌ Ошибка при обработке папки: {}",
        "invalid_chat": "❌ Некорректный чат: {}",
        "stats": "📊 Статистика: отправлено {} из {} сообщений",
        "delay_set": "⏳ Задержка между сообщениями: {} сек.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "delay_between_messages",
                1,
                "Задержка между отправкой сообщений (сек)",
                validator=loader.validators.Integer(minimum=1, maximum=60)
            )
        )
        self.text = None
        self.chats = []
        self.folders = []
        self.interval = 60
        self.task = None
        self.running = False
        self.message = None

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def autochat(self, message):
        """<@ или ID чатов> - Добавить отдельные чаты для рассылки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите чаты через пробел")
        
        self.chats = list(set(args.split()))  # Удаляем дубли
        await utils.answer(message, self.strings["chats_set"].format(', '.join(self.chats)))

    @loader.command()
    async def autofolder(self, message):
        """<названия папок> - Добавить папки для рассылки (через запятую)"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите названия папок через запятую")
        
        self.folders = [f.strip() for f in args.split(",")]
        await utils.answer(message, self.strings["folders_set"].format(', '.join(self.folders)))

    @loader.command()
    async def autotext(self, message):
        """<текст> - Установить текст для рассылки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["no_text"])
        self.text = args
        await utils.answer(message, self.strings["text_set"])

    @loader.command()
    async def autotime(self, message):
        """<секунды> - Интервал между циклами рассылки"""
        args = utils.get_args(message)
        if not args or not args[0].isdigit():
            return await utils.answer(message, "❌ Укажите число в секундах")
        self.interval = int(args[0])
        await utils.answer(message, self.strings["interval_set"].format(self.interval))

    @loader.command()
    async def autodelay(self, message):
        """<секунды> - Задержка между сообщениями"""
        args = utils.get_args(message)
        if not args or not args[0].isdigit():
            return await utils.answer(message, "❌ Укажите число от 1 до 60")
        self.config["delay_between_messages"] = int(args[0])
        await utils.answer(message, self.strings["delay_set"].format(self.config["delay_between_messages"]))

    @loader.command()
    async def autosend(self, message):
        """Включить/выключить рассылку"""
        self.message = message
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            return await utils.answer(message, self.strings["stop_spam"])
        
        if not self.chats and not self.folders:
            return await utils.answer(message, self.strings["no_targets"])
        if not self.text:
            return await utils.answer(message, self.strings["no_text"])

        self.running = True
        self.task = asyncio.create_task(self._autospam())
        await utils.answer(message, self.strings["start_spam"])

    async def _get_all_targets(self):
        """Получает все цели: и чаты, и из папок"""
        targets = []
        
        # Добавляем отдельные чаты
        targets.extend(self.chats)
        
        # Добавляем чаты из папок
        if self.folders:
            dialogs = await self.client.get_dialogs()
            for folder_name in self.folders:
                folder_chats = []
                for dialog in dialogs:
                    if hasattr(dialog, 'folder') and dialog.folder and dialog.folder.title.lower() == folder_name.lower():
                        try:
                            entity = await self.client.get_input_entity(dialog.entity)
                            folder_chats.append(entity)
                        except Exception as e:
                            print(f"[AutoSpammer] Ошибка получения entity: {e}")
                
                if folder_chats:
                    targets.extend(folder_chats)
                    await utils.answer(
                        self.message,
                        self.strings["folder_processing"].format(folder_name, len(folder_chats))
                    )
                else:
                    await utils.answer(
                        self.message,
                        self.strings["folder_error"].format(folder_name)
                    )
        
        return list(set(targets))  # Удаляем дубликаты

    async def _autospam(self):
        while self.running:
            targets = await self._get_all_targets()
            if not targets:
                await utils.answer(self.message, "❌ Нет доступных целей для рассылки!")
                self.running = False
                return
            
            total = len(targets)
            success = 0
            
            for target in targets:
                if not self.running:
                    break
                
                try:
                    await self.client.send_message(target, self.text)
                    success += 1
                    
                    if success % 5 == 0:
                        await utils.answer(
                            self.message,
                            self.strings["stats"].format(success, total)
                        )
                    
                    await asyncio.sleep(self.config["delay_between_messages"])
                except Exception as e:
                    print(f"[AutoSpammer] Ошибка отправки в {target}: {e}")
                    if "InputPeerChat" in str(target):
                        await utils.answer(
                            self.message,
                            self.strings["invalid_chat"].format(target)
                        )
            
            if self.running:
                final_msg = f"🌀 Цикл завершен. Успешно: {success}/{total}"
                if success < total:
                    final_msg += f"\n❌ Не удалось отправить: {total - success}"
                await utils.answer(self.message, final_msg)
                await asyncio.sleep(self.interval)
