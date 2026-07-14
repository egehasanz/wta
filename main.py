import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
LOG_CHANNEL_ID = 1526664676425994260
MUAF_ROL_ID = 1526638053798445156

# Küfür listesini genişlettim ve türetilmiş hallerini de kapsayacak şekilde güncelledim
KUFURLER = [
    "amk", "aq", "orospu", "pic", "siktir", "got", "yavsak", "amina", "sik", 
    "oc", "oç", "yarrak", "yarak", "ibne", "kahpe", "yavşak", "göt", "piç",
    "amına", "amk", "sikim", "sikerim", "siktir", "pezevenk", "ebenin", "ananı"
]

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="WTA Security - Koruma Aktif"))
    print("Bot profesyonel modda aktif!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # Küfür Kontrolü (Gelişmiş Tarama)
    rol_var_mi = any(role.id == MUAF_ROL_ID for role in message.author.roles)
    if not rol_var_mi:
        content = message.content.lower()
        # Herhangi bir küfür mesajın içinde geçiyor mu?
        if any(bad_word in content for bad_word in KUFURLER):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, küfür yasak!", delete_after=5)
            return
            
    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} sunucudan banlandı.")

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    if not yetkili_mi(ctx): return
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} sunucudan atıldı.")

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
    msg = await ctx.send(f"🧹 {miktar} mesaj silindi.", delete_after=3)

@bot.command()
async def uyari(ctx, member: discord.Member, *, sebep="Sebep yok"):
    if not yetkili_mi(ctx): return
    data = dosya_yukle("uyarilar.json")
    m_id = str(member.id)
    data[m_id] = data.get(m_id, 0) + 1
    dosya_kaydet("uyarilar.json", data)
    await ctx.send(f"⚠️ {member.name} uyarıldı! (Toplam: {data[m_id]})")

@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Merkezi", color=discord.Color.blue())
    embed.add_field(name="🔨 Moderasyon", value="`.ban`, `.kick`, `.sustur`, `.temizle`", inline=False)
    embed.add_field(name="⚠️ Uyarılar", value="`.uyari @üye`, `.uyarilar @üye`", inline=False)
    embed.add_field(name="⚙️ Genel", value="`.yetkiekle @üye`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
