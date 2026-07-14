import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
LOG_CHANNEL_ID = 123456789012345678 # Kendi log kanalı ID'ni buraya yaz
KUFURLER = ["amk", "ananı", "anani", "oç", "oc", "sik"] # Buraya filtrelemek istediğin kelimeleri ekle

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
bot = commands.Bot(command_prefix=".", intents=intents)

# --- EVENTLER (LOG, KÜFÜR, HOŞ GELDİN) ---

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="OwO Trades #ACILIS"))
    print("Bot profesyonel modda aktif!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # 1. Küfür Filtresi
    if any(word in message.content.lower() for word in KUFURLER):
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, küfür yasak!")
        return

    # 2. Anti-Spam (Basit)
    # (Not: Gelişmişi için veritabanı gerekir, bu basit bir korumadır)
    
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"👋 Hoş geldin {member.mention}! Sunucuda iyi vakit geçir.")

@bot.event
async def on_member_remove(member):
    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch:
        await log_ch.send(f"🏃 {member.name} sunucudan ayrıldı.")

@bot.event
async def on_message_delete(message):
    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch and not message.author.bot:
        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Yazan", value=message.author.name)
        embed.add_field(name="Mesaj", value=message.content)
        await log_ch.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch:
        if before.channel is None and after.channel is not None:
            await log_ch.send(f"🔊 {member.name}, {after.channel.name} kanalına katıldı.")
        elif before.channel is not None and after.channel is None:
            await log_ch.send(f"🔇 {member.name}, sesli kanaldan ayrıldı.")

# --- DÜZENLİ YARDIM MENÜSÜ ---

@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Merkezi", color=discord.Color.blue())
    
    embed.add_field(name="🔨 Moderasyon", value="`.sustur @üye süre`, `.temizle miktar`, `.ban @üye`, `.kick @üye`", inline=False)
    embed.add_field(name="⚠️ Uyarı Sistemi", value="`.uyari @üye`, `.uyarilar @üye`", inline=False)
    embed.add_field(name="⚙️ Yönetim", value="`.yetkiekle @üye`, `.sunucubilgi`", inline=False)
    
    embed.set_footer(text="Geliştirici: Ege | Profesyonel Güvenlik")
    await ctx.send(embed=embed)

# --- DİĞER KOMUTLAR (sustur, temizle vb. önceki kodlarla aynı) ---
# ... (yetkiekle, sustur, temizle komutlarını buraya eklemeyi unutma) ...

bot.run(os.getenv("BOT_TOKEN"))
