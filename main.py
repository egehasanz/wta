import discord
from discord.ext import commands
import json
import os
import datetime

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
LOG_CHANNEL_ID = 1526664676425994260
MUAF_ROL_ID = 1526638053798445156

# --- INTENTS TANIMLAMA (HATA BURADAN KAYNAKLANIYORDU) ---
intents = discord.Intents.all() 
bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİ YÖNETİMİ ---
def dosya_yukle(filename):
    if not os.path.exists(filename): return {}
    with open(filename, "r") as f: return json.load(f)

# --- EVENTLER ---
@bot.event
async def on_ready():
    print(f"{bot.user} - WTA Security Aktif!")

@bot.event
async def on_message(message):
    if message.author.bot or any(role.id == MUAF_ROL_ID for role in message.author.roles):
        await bot.process_commands(message)
        return

    # Anti-Link ve CapsLock
    if "http" in message.content.lower():
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention}, link paylaşmak yasak!", delete_after=5)
    elif len(message.content) > 15 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7:
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, büyük harf kullanımı yasak!", delete_after=5)
    
    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} banlandı.")

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} atıldı.")

@bot.command()
async def sustur(ctx, member: discord.Member, dakika: int, *, sebep="Sebep yok"):
    until = discord.utils.utcnow() + datetime.timedelta(minutes=dakika)
    await member.timeout(until, reason=sebep)
    await ctx.send(f"🤐 {member.name} {dakika} dakika susturuldu.")

@bot.command()
async def temizle(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 {miktar} mesaj silindi.", delete_after=3)

@bot.command()
async def userinfo(ctx, member: discord.Member):
    embed = discord.Embed(title=f"👤 {member.name} Bilgileri", color=0x3498db)
    embed.add_field(name="Hesap Oluşturulma", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Sunucuya Katılım", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Paneli", description="Tüm komutlar:", color=0x9b59b6)
    embed.add_field(name="🔒 Güvenlik", value="`.lockdown`, `.userinfo`", inline=False)
    embed.add_field(name="🔨 Moderasyon", value="`.ban`, `.kick`, `.sustur`, `.temizle`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
