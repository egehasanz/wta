import discord
from discord.ext import commands, tasks
import os
import asyncio
import itertools

# Bot Altyapısı
class WTA_Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="/", intents=intents, help_command=None)
        self.statuses = itertools.cycle([
            discord.Game("🛡️ WTA Security"),
            discord.Activity(type=discord.ActivityType.watching, name="Tickets & Logs"),
            discord.Activity(type=discord.ActivityType.listening, name="/ticket & /ban")
        ])

    async def setup_hook(self):
        # Cogs yükleme
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Modül Yüklendi: {filename}')
                except Exception as e:
                    print(f'❌ Modül Hatası {filename}: {e}')
        
        # Slash komutlarını senkronize et
        await self.tree.sync()

    @tasks.loop(seconds=10)
    async def change_status(self):
        await self.change_presence(activity=next(self.statuses))

    async def on_ready(self):
        self.change_status.start()
        print("="*30)
        print(f"🤖 Bot Adı: {self.user.name}")
        print(f"🆔 Bot ID: {self.user.id}")
        print(f"🚀 WTA Security Süper Seviye Aktif!")
        print("="*30)

bot = WTA_Bot()

async def main():
    async with bot:
        await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
