import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
DATA_FILE = "yetkiler.json"
WARN_FILE = "uyarilar.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİ YÖNETİMİ ---
def dosya_yukle(filename):
    if not os.path.exists(filename): return {} if filename == WARN_FILE else [OWNER_ID]
    with open(filename, "r") as f: return json.load(f)

def dosya_kaydet(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

def yetkili_mi(ctx):
    users = dosya_yukle(DATA_FILE)
    return ctx.author.id in users or ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="OwO Trades #ACILIS"))
    print(f"{bot.user} başarıyla başlatıldı.")

# --- KOMUTLAR ---

@bot.command()
async def yetkiekle(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID: return
    data = dosya_yukle(DATA_FILE)
    if member.id not in data:
        data.append(member.id)
        dosya_kaydet(DATA_FILE, data)
        await ctx.send(f"✅ {member.name} artık yetkili.")

@bot.command(name="uyari")
async def uyari(ctx, member: discord.Member, *, sebep="Sebep yok"):
    if not yetkili_mi(ctx): return
    data = dosya_yukle(WARN_FILE)
    m_id = str(member.id)
    data[m_id] = data.get(m_id, 0) + 1
    dosya_kaydet(WARN_FILE, data)
    msg = await ctx.send("⚠️ İşleniyor...")
    await asyncio.sleep(0.5)
    await msg.edit(content=f"⚠️ {member.name} uyarıldı! (Toplam: {data[m_id]})")

@bot.command(name="uyarilar")
async def uyarilar(ctx, member: discord.Member):
    if not yetkili_mi(ctx): return
    data = dosya_yukle(WARN_FILE)
    sayi = data.get(str(member.id), 0)
    await ctx.send(f"📊 {member.name} kullanıcısının toplam {sayi} uyarısı var.")

@bot.command()
async def sustur(ctx, member: discord.Member, dakika: int, *, sebep="Sebep yok"):
    if not yetkili_mi(ctx): return
    msg = await ctx.send(f"⏳ {member.name} susturuluyor...")
    try:
        until = discord.utils.utcnow() + datetime.timedelta(minutes=dakika)
        await member.timeout(until, reason=sebep)
        await msg.edit(content=f"🤐 {member.name} {dakika} dakika susturuldu!")
    except:
        await msg.edit(content=f"❌ Hata: Yetkilerimi kontrol et!")

@bot.command()
async def temizle(ctx, miktar: int):
    if not yetkili_mi(ctx): return
    msg = await ctx.send(f"🧹 {miktar} mesaj siliniyor...")
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=miktar + 2)
    final = await ctx.send("✅ Başarıyla temizlendi!")
    await asyncio.sleep(2)
    await final.delete()

@bot.command(name="yardim")
async def yardim(ctx):
    # Yetkili olup olmadığına bakılmaksızın herkes görebilir
    embed = discord.Embed(title="🤖 Komut Listesi", color=discord.Color.purple())
    embed.add_field(name="Mod Komutları", value=".sustur @üye süre, .uyari @üye, .uyarilar @üye, .temizle miktar", inline=False)
    embed.add_field(name="Yönetim", value=".yetkiekle @üye", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
