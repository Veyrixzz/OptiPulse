# meta developer: @OptiPulseMod
# scope: user
# requires: hikka

"""
AutoSpammer Module for Hikka Userbot
Рассылка сообщений в выбранные чаты (HTML-разметка поддерживается)
"""

from hikka import loader, utils
import asyncio

@loader.tds
class AutoSenderMod(loader.Module):
    """Авторассылка сообщений от вашего аккаунта"""

    strings = {
        "name": "AutoSender",
        "start": "✅ Рассылка запущена!",
        "stop": "⛔ Рассылка остановлена",
        "no_text": "❌ Не указан текст",
        "no_targets": "❌ Не указаны цели (чаты)",
        "added_chats": "💬 Добавлены чаты: {}",
        "text_set": "📝 Текст установлен",
        "delay_set": "⏱ Задержка: {} мин",
        "sending_stats": "📤 Отправлено {}/{}",
        "error": "⚠️ Ошибка в {}: {}",
    }

    def __init__(self):
        self.text = None
        self.chats = []
        self.delay = 1  # в минутах
        self.running = False
        self.task = None

    @loader.command()
    async def aspam_text(self, message):
        """<HTML-текст> — Установить текст сообщения"""
        text = utils.get_args_raw(message)
        if not text:
            return await utils.answer(message, self.strings("no_text"))
        self.text = text
        await utils.answer(message, self.strings("text_set"))

    @loader.command()
    async def aspam_chats(self, message):
        """<@юзер/ID> — Добавить чаты (через пробел)"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Укажите чаты через пробел")
        self.chats = list(set(args.split()))
        await utils.answer(message, self.strings("added_chats").format(len(self.chats)))

    @loader.command()
    async def aspam_delay(self, message):
        """<мин> — Задержка между сообщениями (в минутах, без ограничений)"""
        args = utils.get_args_raw(message)
        try:
            d = float(args)
            self.delay = d
            await utils.answer(message, self.strings("delay_set").format(d))
        except:
            await utils.answer(message, "❌ Неверный ввод")

    @loader.command()
    async def aspam_start(self, message):
        """🚀 Старт рассылки"""
        if not self.text:
            return await utils.answer(message, self.strings("no_text"))
        if not self.chats:
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

    async def _spam_loop(self, message):
        total = len(self.chats)
        success = 0
        while self.running:
            for chat in self.chats:
                if not self.running:
                    return
                try:
                    entity = await self.client.get_entity(chat)
                    await self.client.send_message(entity, self.text, parse_mode="html")
                    success += 1
                    await utils.answer(message, self.strings("sending_stats").format(success, total))
                    await asyncio.sleep(self.delay * 60)
                except Exception as e:
                    await utils.answer(message, self.strings("error").format(chat, str(e)))
