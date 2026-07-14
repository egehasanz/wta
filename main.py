import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
LOG_CHANNEL_ID = 0 # Buraya kanal ID'ni yaz
KUFURLER = ["kufur1", "kufur2"] 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİ YÖNETİMİ ---
def dosya_yukle(filename):
    if not os.path.exists(filename): return {} if filename == "uyarilar.json" else [OWNER_ID]
    with open(filename, "r") as f: return json.load(f)

def dosya_kaydet(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

def yetkili_mi(ctx):
    users = dosya_yukle("yetkiler.json")
    return ctx.author.id in users or ctx.author.id == OWNER_ID

# --- EVENTLER ---
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="OwO Trades #ACILIS"))
    print("Bot profesyonel modda aktif!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    if any(word in message.content.lower() for word in KUFURLER):
        await message.delete()
        await message.channel.send(f"⚠️ {message.author.mention}, küfür yasak!")
        return
    await bot.process_commands(message)

# --- KOMUTLAR ---

@bot.command()
async def yetkiekle(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID: return
    data = dosya_yukle("yetkiler.json")
    if member.id not in data:
        data.append(member.id)
        dosya_kaydet("yetkiler.json", data)
        await ctx.send(f"✅ {member.name} artık yetkili.")

@bot.command()
async def uyari(ctx, member: discord.Member, *, sebep="Sebep yok"):
    if not yetkili_mi(ctx): return
    data = dosya_yukle("uyarilar.json")
    m_id = str(member.id)
    data[m_id] = data.get(m_id, 0) + 1
    dosya_kaydet("uyarilar.json", data)
    await ctx.send(f"⚠️ {member.name} uyarıldı! (Toplam: {data[m_id]})")

@bot.command(name="uyarilar")
async def uyarilar(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    data = dosya_yukle("uyarilar.json")
    sayi = data.get(str(member.id), 0)
    await ctx.send(f"📊 {member.name} kullanıcısının {sayi} uyarısı var.")

@bot.command()
async def sustur(ctx, member: discord.Member, dakika: int, *, sebep="Sebep yok"):
    if not yetkili_mi(ctx): return
    until = discord.utils.utcnow() + datetime.timedelta(minutes=dakika)
    await member.timeout(until, reason=sebep)
    await ctx.send(f"🤐 {member.name} {dakika} dakika susturuldu.")

@bot.command()
async def temizle(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    await ctx.channel.purge(limit=miktar + 1)
    msg = await ctx.send(f"🧹 {miktar} mesaj silindi.")
    await asyncio.sleep(2)
    await msg.delete()

@bot.command()
async def sunucubilgi(ctx):
    if not yetkili_mi(ctx): return
    embed = discord.Embed(title="📊 Sunucu Bilgisi", color=discord.Color.green())
    embed.add_field(name="Üye Sayısı", value=ctx.guild.member_count)
    await ctx.send(embed=embed)

@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Merkezi", color=discord.Color.blue())
    embed.add_field(name="🔨 Moderasyon", value="`.sustur @üye süre`, `.temizle miktar`", inline=False)
    embed.add_field(name="⚠️ Uyarılar", value="`.uyari @üye`, `.uyarilar @üye`", inline=False)
    embed.add_field(name="⚙️ Genel", value="`.sunucubilgi`, `.yetkiekle @üye`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
