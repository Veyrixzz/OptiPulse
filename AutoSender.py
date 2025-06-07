# meta developer: @OptiPulseMod

"""
AutoSpammer Module for Userbot (работает от вашего аккаунта)
"""

from hikka import loader, utils
import asyncio
from telethon.tl.types import Dialog, InputPeerChannel, InputPeerChat

@loader.tds
class AutoSenderMod(loader.Module):
    """Авторассылка сообщений от вашего аккаунта"""

    strings = {
        "name": "AccountSpammer",
        "start": "✅ Рассылка запущена от вашего аккаунта",
        "stop": "⛔ Рассылка остановлена",
        "no_text": "❌ Не указан текст сообщения",
        "no_targets": "❌ Не указаны чаты/папки",
        "added_chats": "💬 Добавлены чаты: {}",
        "added_folders": "📂 Добавлены папки: {}",
        "text_set": "📝 Текст установлен",
        "interval_set": "⏱ Интервал: {} сек",
        "delay_set": "⏳ Задержка: {} сек",
        "folder_stats": "📊 В папке '{}' найдено {} чатов",
        "sending_stats": "📤 Отправлено {}/{} сообщений",
        "error": "❌ Ошибка в {}: {}"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(  # Fixed: Added closing parenthesis
            loader.ConfigValue(
                "delay",
                1,
                "Задержка между сообщениями",
                validator=loader.validators.Integer(minimum=1, maximum=10)
            )
        )
        self.text = None
        self.chats = []
        self.folders = []
        self.interval = 60
        self.task = None
        self.is_active = False

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def aspam_chats(self, message):
        """<@username/id> - Добавить чаты для рассылки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите чаты через пробел")
        
        self.chats = list(set(args.split()))
        await utils.answer(message, self.strings["added_chats"].format(len(self.chats)))

    @loader.command()
    async def aspam_folders(self, message):
        """<названия> - Добавить папки для рассылки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите папки через запятую")
        
        self.folders = [f.strip() for f in args.split(",")]
        await utils.answer(message, self.strings["added_folders"].format(len(self.folders)))

    @loader.command()
    async def aspam_text(self, message):
        """<текст> - Установить текст"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["no_text"])
        
        self.text = args
        await utils.answer(message, self.strings["text_set"])

    @loader.command()
    async def aspam_start(self, message):
        """Запустить рассылку"""
        if not self.text:
            return await utils.answer(message, self.strings["no_text"])
        if not self.chats and not self.folders:
            return await utils.answer(message, self.strings["no_targets"])

        self.is_active = True
        self.task = asyncio.create_task(self._spam_loop(message))
        await utils.answer(message, self.strings["start"])

    @loader.command()
    async def aspam_stop(self, message):
        """Остановить рассылку"""
        self.is_active = False
        if self.task:
            self.task.cancel()
        await utils.answer(message, self.strings["stop"])

    async def _get_chats_in_folder(self, folder_name):
        """Находит все чаты в указанной папке"""
        try:
            dialogs = await self.client.get_dialogs()
            folder_chats = []
            
            for dialog in dialogs:
                if (hasattr(dialog, 'folder') and 
                    dialog.folder and 
                    dialog.folder.title.lower() == folder_name.lower()):
                    
                    try:
                        entity = await self.client.get_input_entity(dialog.entity)
                        folder_chats.append(entity)
                    except Exception as e:
                        print(f"Error getting entity: {e}")
            
            return folder_chats
        except Exception as e:
            print(f"Folder error: {e}")
            return []

    async def _spam_loop(self, message):
        while self.is_active:
            # Собираем все цели
            targets = []
            
            # Добавляем отдельные чаты
            targets.extend(self.chats)
            
            # Добавляем чаты из папок
            for folder in self.folders:
                folder_chats = await self._get_chats_in_folder(folder)
                if folder_chats:
                    targets.extend(folder_chats)
                    await utils.answer(
                        message,
                        self.strings["folder_stats"].format(folder, len(folder_chats))
                    )
            
            if not targets:
                await utils.answer(message, self.strings["no_targets"])
                self.is_active = False
                return
            
            # Отправка сообщений
            total = len(targets)
            success = 0
            
            for target in targets:
                if not self.is_active:
                    break
                
                try:
                    await self.client.send_message(target, self.text)
                    success += 1
                    
                    if success % 5 == 0 or success == total:
                        await utils.answer(
                            message,
                            self.strings["sending_stats"].format(success, total)
                        )
                    
                    await asyncio.sleep(self.config["delay"])
                except Exception as e:
                    await utils.answer(
                        message,
                        self.strings["error"].format(target, str(e))
                    )
            
            # Пауза между циклами
            if self.is_active:
                await asyncio.sleep(self.interval)  # Fixed: Removed extra parenthesis
