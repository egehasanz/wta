import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
LOG_CHANNEL_ID = 1526664676425994260  # Log kanalın buraya eklendi
MUAF_ROL_ID = 1526638053798445156    # Muaf rol
KUFURLER = ["amk", "aq", "orospu", "piç", "siktir", "göt", "yavşak", "amına", "sik"] 

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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="WTA Security - Aktif"))
    print("Bot profesyonel modda aktif!")

# Küfür Filtresi
@bot.event
async def on_message(message):
    if message.author.bot: return
    rol_var_mi = any(role.id == MUAF_ROL_ID for role in message.author.roles)
    if not rol_var_mi:
        if any(word in message.content.lower() for word in KUFURLER):
            await message.delete()
            await message.channel.send(f"⚠️ {message.author.mention}, küfür yasak!")
            return
    await bot.process_commands(message)

# Log Sistemleri
@bot.event
async def on_message_delete(message):
    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch and not message.author.bot:
        embed = discord.Embed(title="🗑️ Mesaj Silindi", color=discord.Color.red())
        embed.add_field(name="Yazan", value=message.author.name)
        embed.add_field(name="Mesaj", value=message.content[:1024])
        await log_ch.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch:
        if before.channel is None and after.channel is not None:
            await log_ch.send(f"🔊 {member.name}, {after.channel.name} kanalına katıldı.")
        elif before.channel is not None and after.channel is None:
            await log_ch.send(f"🔇 {member.name}, sesli kanaldan ayrıldı.")

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
async def unban(ctx, user_id: int):
    if not yetkili_mi(ctx): return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"🔓 {user.name} banı kaldırıldı.")
    except:
        await ctx.send("❌ Kullanıcı bulunamadı.")

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

@bot.command(name="yardim")
async def yardim(ctx):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Merkezi", color=discord.Color.blue())
    embed.add_field(name="🔨 Moderasyon", value="`.ban`, `.kick`, `.unban ID`, `.sustur`, `.temizle`", inline=False)
    embed.add_field(name="⚠️ Uyarılar", value="`.uyari @üye`, `.uyarilar @üye`", inline=False)
    embed.add_field(name="⚙️ Yönetim", value="`.yetkiekle @üye`", inline=False)
    await ctx.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
