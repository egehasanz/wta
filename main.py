import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
DATA_FILE = "authorized_users.json"
WARN_FILE = "warnings.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİ YÖNETİMİ ---
def load_json(filename):
    if not os.path.exists(filename): return {} if filename == WARN_FILE else [OWNER_ID]
    with open(filename, "r") as f: return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- KONTROLLER ---
def is_authorized(ctx):
    users = load_json(DATA_FILE)
    return ctx.author.id in users or ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="OwO Trades #AÇILIŞ"))
    print(f"{bot.user} aktif!")

# --- KOMUTLAR ---

@bot.command()
async def yetkiekle(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID: return
    data = load_json(DATA_FILE)
    if member.id not in data:
        data.append(member.id)
        save_json(DATA_FILE, data)
        await ctx.send(f"✅ {member.name} yetkilendirildi.")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    warns = load_json(WARN_FILE)
    m_id = str(member.id)
    warns[m_id] = warns.get(m_id, 0) + 1
    save_json(WARN_FILE, warns)
    await ctx.send(f"⚠️ **{member.name}** uyarıldı! (Toplam: {warns[m_id]})")

@bot.command()
async def uyarılar(ctx, member: discord.Member):
    if not is_authorized(ctx): return
    warns = load_json(WARN_FILE)
    count = warns.get(str(member.id), 0)
    await ctx.send(f"📊 **{member.name}** adlı kişinin toplam **{count}** uyarısı bulunuyor.")

@bot.command()
async def mute(ctx, member: discord.Member, minutes: int, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)
    await ctx.send(f"🤐 **{member.name}**, {minutes} dakika susturuldu.")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.name} banlandı.")

@bot.command()
async def temizle(ctx, amount: int):
    if not is_authorized(ctx): return
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 {amount} mesaj silindi.", delete_after=3)

@bot.command()
async def yardım(ctx):
    if not is_authorized(ctx): return
    embed = discord.Embed(title="🤖 Yardım Menüsü", color=discord.Color.purple())
    embed.add_field(name="🔨 Moderasyon", value="`.ban` `.kick` `.mute` `.warn` `.uyarılar @üye` `.temizle`", inline=False)
    embed.add_field(name="🛡️ Yetki", value="`.yetkiekle` `.rolver` `.rolal`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
