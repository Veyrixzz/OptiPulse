# meta developer: @OptiPulseMod

from .. import loader, utils
import requests

class RobloxInfoMod(loader.Module):
    strings = {"name": "RBIroblox"}

    @loader.command()
    async def rbi(self, m):
        """<ник> — Получить инфу об игроке Roblox"""
        username = utils.get_args_raw(m)
        if not username:
            return await m.edit("Укажи ник в Roblox")
user_res = requests.post(
    "https://users.roblox.com/v1/usernames/users",
    json={"usernames": [username], "excludeBannedUsers": False}
)

        )
        if user_res.status_code != 200 or not user_res.json().get("data"):
            return await m.edit("Пользователь не найден :(")
        
        user = user_res.json()["data"][0]
        user_id = user["id"]

        # Получение полной инфы
        profile = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
        presence = requests.get("https://presence.roblox.com/v1/presence/users", json={"userIds": [user_id]}).json()
        online_status = presence.get("userPresences", [{}])[0]

        # Формируем инфу
        name = profile.get("name")
        display = profile.get("displayName")
        created = profile.get("created", "")[:10]
        desc = profile.get("description", "Без описания")
        profile_url = f"https://www.roblox.com/users/{user_id}/profile"
        avatar = f"https://www.roblox.com/headshot-thumbnail/image?userId={user_id}&width=150&height=150&format=png"

        status_map = {
            0: "🔘 Не в сети",
            1: "🟢 Онлайн",
            2: f"🎮 В игре: {online_status.get('lastLocation')}",
            3: f"📱 В студии: {online_status.get('lastLocation')}"
        }

        status = status_map.get(online_status.get("userPresenceType", 0), "❓ Неизвестно")

        text = f"""
👤 <b>{display}</b> (@{name})
🆔 <code>{user_id}</code>
🗓 Регистрация: <b>{created}</b>
💬 Описание: <i>{desc}</i>

{status}
🔗 <a href="{profile_url}">Открыть профиль</a>
"""
        await m.client.send_file(m.chat_id, avatar, caption=text, parse_mode="html")
        await m.delete()
