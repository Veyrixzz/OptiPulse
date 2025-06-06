from hikka import loader, utils
import asyncio

@loader.tds
class AutoSenderMod(loader.Module):
    strings = {
        "name": "AutoSpammer",
        "start_spam": "✅ Авторассылка запущена.",
        "stop_spam": "⛔ Авторассылка остановлена.",
        "interval_set": "⏱ Интервал установлен: {} секунд.",
        "text_set": "📝 Текст сообщения установлен.",
        "targets_set": "🎯 Цели установлены: {}.",
        "no_targets": "❌ Не указаны цели (группы/папки).",
        "no_text": "❌ Не указан текст сообщения.",
        "folder_error": "❌ Ошибка при обработке папки: {}",
    }

    def __init__(self):
        self.text = None
        self.targets = []
        self.interval = 60
        self.task = None
        self.running = False

    async def autogroupcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_targets"))
        
        self.targets = args.split()
        await utils.answer(message, self.strings("targets_set").format(', '.join(self.targets)))

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
        if not self.targets:
            return await utils.answer(message, self.strings("no_targets"))
        if not self.text:
            return await utils.answer(message, self.strings("no_text"))

        self.running = True
        self.task = asyncio.create_task(self._autospam())
        await utils.answer(message, self.strings("start_spam"))

    async def _get_chats_from_folder(self, folder_link):
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
                for target in self.targets:
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
