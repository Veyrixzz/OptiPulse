# meta developer: @OptiPulseMod
# scope: hikka_only
# scope: hikka_min 1.6.2

"""
FolderLinkExtractor Module for Hikka Userbot

Copyright (c) 2025 @OptiPulseMod
"""

from hikka import loader, utils
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.types import ChatInviteAlready
import re

@loader.tds
class FolderLinkExtractorMod(loader.Module):
    """Извлекает чаты из папки по ссылке"""
    
    strings = {
        "name": "FolderLinkExtractor",
        "no_args": "❌ Укажите ссылку на папку (например: https://t.me/addlist/gZYzUWty_K84NGMy)",
        "invalid_link": "❌ Неверный формат ссылки на папку",
        "processing": "🔍 Обрабатываю ссылку на папку...",
        "success": "✅ Успешно получены чаты из папки:",
        "chat_info": "├─ {title} (ID: {id})",
        "error": "❌ Ошибка при обработке папки: {}",
        "not_member": "⚠️ Вы не состоите в этой папке или она не существует"
    }

    async def flinkcmd(self, message):
        """<ссылка_на_папку> - Получить чаты из папки"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings("no_args"))

        match = re.match(r"https?://t\.me/addlist/([a-zA-Z0-9_-]+)", args)
        if not match:
            return await utils.answer(message, self.strings("invalid_link"))

        hash_link = match.group(1)
        await utils.answer(message, self.strings("processing"))

        try:
            invite = await self.client(CheckChatInviteRequest(hash_link))
            
            if not isinstance(invite, ChatInviteAlready):
                return await utils.answer(message, self.strings("not_member"))

            result = []
            for chat in invite.chats:
                result.append({
                    "id": chat.id,
                    "title": getattr(chat, 'title', 'Без названия')
                })

            if not result:
                return await utils.answer(message, self.strings("not_member"))

            response = [self.strings("success")]
            for chat in result:
                response.append(
                    self.strings("chat_info").format(
                        title=chat["title"],
                        id=chat["id"]
                    )
                )
            
            await utils.answer(message, "\n".join(response))
            
        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))
