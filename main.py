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

def is_authorized(ctx):
    users = load_json(DATA_FILE)
    return ctx.author.id in users or ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="OwO Trades #AÇILIŞ")
    await bot.change_presence(activity=activity)
    print(f"{bot.user} başarıyla başlatıldı.")

# --- KOMUTLAR ---

@bot.command()
async def yetkiekle(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID: return
    data = load_json(DATA_FILE)
    if member.id not in data:
        data.append(member.id)
        save_json(DATA_FILE, data)
        await ctx.send(f"✅ {member.name} artık yetkili.")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    warns = load_json(WARN_FILE)
    m_id = str(member.id)
    warns[m_id] = warns.get(m_id, 0) + 1
    save_json(WARN_FILE, warns)
    msg = await ctx.send("⚠️ İşleniyor...")
    await asyncio.sleep(0.5)
    await msg.edit(content=f"⚠️ {member.name} uyarıldı! (Toplam: {warns[m_id]})")

@bot.command(name="uyarilar")
async def uyarilar(ctx, member: discord.Member):
    if not is_authorized(ctx): return
    warns = load_json(WARN_FILE)
    count = warns.get(str(member.id), 0)
    await ctx.send(f"📊 {member.name} kullanıcısının toplam {count} uyarısı var.")

@bot.command()
async def mute(ctx, member: discord.Member, minutes: int, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    msg = await ctx.send(f"⏳ {member.name} susturuluyor...")
    try:
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        await msg.edit(content=f"🤐 {member.name} {minutes} dakika susturuldu!")
    except Exception as e:
        await msg.edit(content=f"❌ Hata: Yetkilerimi kontrol et!")

@bot.command()
async def temizle(ctx, amount: int):
    if not is_authorized(ctx): return
    msg = await ctx.send(f"🧹 {amount} mesaj siliniyor...")
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=amount + 2)
    final = await ctx.send("✅ Başarıyla temizlendi!")
    await asyncio.sleep(2)
    await final.delete()

@bot.command(name="yardim")
async def yardim(ctx):
    if not is_authorized(ctx): return
    embed = discord.Embed(title="🤖 Bot Komut Listesi", color=discord.Color.purple())
    embed.add_field(name="Mod Komutları", value=".ban, .kick, .mute, .warn, .uyarilar, .temizle", inline=False)
    embed.add_field(name="Yetki Komutları", value=".yetkiekle, .rolver, .rolal, .sunucubilgi", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
