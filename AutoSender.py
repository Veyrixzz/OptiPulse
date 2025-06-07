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
        "error": "❌ Ошибка в {}: {}",
        "folder_error": "❌ Ошибка в папке '{}': {}",
        "invalid_delay": "❌ Задержка должна быть от 1 до 10 секунд",
        "invalid_interval": "❌ Интервал должен быть от 10 секунд"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "delay",
                1,
                "Задержка между сообщениями",
                validator=loader.validators.Integer(minimum=1, maximum=10)
            ),
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
    async def aspam_delay(self, message):
        """<секунды> - Установить задержку между сообщениями (1-10 сек)"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите задержку в секундах")
        
        try:
            delay = int(args)
            if delay < 1 or delay > 10:
                return await utils.answer(message, self.strings["invalid_delay"])
            
            self.config["delay"] = delay
            await utils.answer(message, self.strings["delay_set"].format(delay))
        except ValueError:
            await utils.answer(message, "❌ Укажите число от 1 до 10")

    @loader.command()
    async def aspam_interval(self, message):
        """<секунды> - Установить интервал между циклами"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите интервал в секундах")
        
        try:
            interval = int(args)
            if interval < 10:
                return await utils.answer(message, self.strings["invalid_interval"])
            
            self.interval = interval
            await utils.answer(message, self.strings["interval_set"].format(interval))
        except ValueError:
            await utils.answer(message, "❌ Укажите число (минимум 10)")

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
            self.task = None
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
            
            return folder_chats, None
        except Exception as e:
            return [], str(e)

    async def _spam_loop(self, message):
        while self.is_active:
            targets = []
            
            targets.extend(self.chats)
            
            for folder in self.folders:
                folder_chats, error = await self._get_chats_in_folder(folder)
                if error:
                    await utils.answer(
                        message,
                        self.strings["folder_error"].format(folder, error)
                    )
                elif folder_chats:
                    targets.extend(folder_chats)
                    await utils.answer(
                        message,
                        self.strings["folder_stats"].format(folder, len(folder_chats))
            
            if not targets:
                await utils.answer(message, self.strings["no_targets"])
                self.is_active = False
                return
            
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
            
            if self.is_active:
                await utils.answer(
                    message,
                    f"⏳ Следующий цикл через {self.interval} сек"
                )
                await asyncio.sleep(self.interval)
