import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
LOG_CHANNEL_ID = 1526664676425994260 # Buraya kanal ID'ni yaz
KUFURLER = KUFURLER = [
    "amk", "aq", "orospu", "piç", "siktir", "göt", "yavşak", 
    "amına", "sik", "sikim", "sikerim", "pezevenk", "ebenin", 
    "oc", "oç", "yarrak", "amk.", "aq.", "piç.", "siktir."]

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

# --- KOMUTLAR ---

@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} sunucudan banlandı! Sebep: {sebep}")

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} sunucudan atıldı! Sebep: {sebep}")

@bot.command()
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"🔓 {user.name} kullanıcısının banı kaldırıldı.")
    except Exception as e:
        await ctx.send("❌ Kullanıcı bulunamadı veya banlı değil.")

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

@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Merkezi", color=discord.Color.blue())
    embed.add_field(name="🔨 Moderasyon", value="`.ban @üye`, `.kick @üye`, `.unban ID`, `.sustur @üye süre`, `.temizle miktar`", inline=False)
    embed.add_field(name="⚠️ Uyarılar", value="`.uyari @üye`, `.uyarilar @üye`", inline=False)
    embed.add_field(name="⚙️ Genel", value="`.yetkiekle @üye`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
