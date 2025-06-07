# meta developer: @OptiPulseMod
# scope: user
# requires: hikka

"""
AutoSpammer Module for Hikka Userbot
Рассылка сообщений в выбранные чаты и папки
"""

from hikka import loader, utils
from telethon.tl.types import Dialog
import asyncio

@loader.tds
class AutoSenderMod(loader.Module):
    """Авторассылка сообщений от вашего аккаунта"""

    strings = {
        "name": "AutoSender",
        "start": "✅ Рассылка запущена!",
        "stop": "⛔ Рассылка остановлена",
        "no_text": "❌ Не указан текст",
        "no_targets": "❌ Не указаны цели (чаты или папки)",
        "added_chats": "💬 Добавлены чаты: {}",
        "added_folders": "📂 Добавлены папки: {}",
        "text_set": "📝 Текст установлен",
        "delay_set": "⏱ Задержка: {} сек",
        "interval_set": "🔁 Интервал: {} сек",
        "folder_stats": "📊 В папке '{}' найдено {} чатов",
        "sending_stats": "📤 Отправлено {}/{}",
        "error": "⚠️ Ошибка в {}: {}",
        "invalid_delay": "❗ Задержка от 1 до 10 сек",
        "invalid_interval": "❗ Интервал от 10 сек",
    }

    def __init__(self):
        self.text = None
        self.chats = []
        self.folders = []
        self.delay = 2
        self.interval = 60
        self.running = False
        self.task = None

    @loader.command()
    async def aspam_text(self, message):
        """<текст> — Установить текст сообщения"""
        text = utils.get_args_raw(message)
        if not text:
            return await utils.answer(message, self.strings("no_text"))
        self.text = text
        await utils.answer(message, self.strings("text_set"))

    @loader.command()
    async def aspam_chats(self, message):
        """<@юзер/ID> — Добавить чаты"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите чаты через пробел")
        self.chats = list(set(args.split()))
        await utils.answer(message, self.strings("added_chats").format(len(self.chats)))

    @loader.command()
    async def aspam_folders(self, message):
        """<название,название> — Добавить папки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите названия папок через запятую")
        self.folders = [f.strip() for f in args.split(",")]
        await utils.answer(message, self.strings("added_folders").format(len(self.folders)))

    @loader.command()
    async def aspam_delay(self, message):
        """<сек> — Задержка между сообщениями"""
        args = utils.get_args_raw(message)
        try:
            d = int(args)
            if not 1 <= d <= 10:
                return await utils.answer(message, self.strings("invalid_delay"))
            self.delay = d
            await utils.answer(message, self.strings("delay_set").format(d))
        except:
            await utils.answer(message, "❌ Неверный ввод")

    @loader.command()
    async def aspam_interval(self, message):
        """<сек> — Интервал между циклами"""
        args = utils.get_args_raw(message)
        try:
            i = int(args)
            if i < 10:
                return await utils.answer(message, self.strings("invalid_interval"))
            self.interval = i
            await utils.answer(message, self.strings("interval_set").format(i))
        except:
            await utils.answer(message, "❌ Неверный ввод")

    @loader.command()
    async def aspam_start(self, message):
        """🚀 Старт рассылки"""
        if not self.text:
            return await utils.answer(message, self.strings("no_text"))
        if not self.chats and not self.folders:
            return await utils.answer(message, self.strings("no_targets"))
        if self.running:
            return await utils.answer(message, "❗ Уже работает")

        self.running = True
        self.task = asyncio.create_task(self._spam_loop(message))
        await utils.answer(message, self.strings("start"))

    @loader.command()
    async def aspam_stop(self, message):
        """🛑 Остановить рассылку"""
        self.running = False
        if self.task:
            self.task.cancel()
        await utils.answer(message, self.strings("stop"))

    async def _get_folder_chats(self, folder_name):
        """Поиск чатов в папке по имени"""
        dialogs = await self.client.get_dialogs()
        results = []
        for dialog in dialogs:
            if isinstance(dialog, Dialog):
                folder = getattr(dialog, 'folder', None)
                if folder and folder.title.lower() == folder_name.lower():
                    results.append(dialog.entity)
        return results

    async def _spam_loop(self, message):
        while self.running:
            targets = list(self.chats)
            for folder in self.folders:
                try:
                    chats = await self._get_folder_chats(folder)
                    targets.extend(chats)
                    await utils.answer(message, self.strings("folder_stats").format(folder, len(chats)))
                except Exception as e:
                    await utils.answer(message, self.strings("error").format(folder, str(e)))

            total = len(targets)
            success = 0
            for chat in targets:
                if not self.running:
                    return
                try:
                    entity = await self.client.get_entity(chat)
                    await self.client.send_message(entity, self.text)
                    success += 1
                    if success % 5 == 0 or success == total:
                        await utils.answer(message, self.strings("sending_stats").format(success, total))
                    await asyncio.sleep(self.delay)
                except Exception as e:
                    await utils.answer(message, self.strings("error").format(chat, str(e)))

            if self.running:
                await asyncio.sleep(self.interval)
