import discord
from discord.ext import commands
import os
import asyncio

# Prefix artık kullanılmayacağı için boş geçiyoruz
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

async def load_extensions():
    # cogs klasöründeki dosyaları yükler
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await bot.tree.sync() # Slash komutlarını senkronize eder
    print(f"🚀 {bot.user} - WTA Security Aktif!")

async def main():
    await load_extensions()
    await bot.start(os.getenv("BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
