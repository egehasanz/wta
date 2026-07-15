import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json
import os

# --- AYARLAR ---
LOG_CHANNEL_ID = 1526664676425994260
WELCOME_CHANNEL_ID = 1526706539614699591
XP_FILE = "xp_data.json"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- XP VE LOG YARDIMCI ---
def xp_yukle():
    if not os.path.exists(XP_FILE): return {}
    with open(XP_FILE, "r") as f: return json.load(f)

def xp_kaydet(data):
    with open(XP_FILE, "w") as f: json.dump(data, f, indent=4)

async def log_gonder(guild, baslik, detay):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=f"🛡️ {baslik}", description=detay, color=discord.Color.red())
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WTA Security - Tüm sistemler (Log + XP) aktif!")

# --- MESAJ VE XP ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # Basit XP Sistemi
    data = xp_yukle()
    user_id = str(message.author.id)
    data[user_id] = data.get(user_id, 0) + 1
    xp_kaydet(data)
    
    await bot.process_commands(message)

# --- SLASH KOMUTLARI ---
@bot.tree.command(name="xp", description="Kendi XP'ni gör.")
async def xp(interaction: discord.Interaction):
    data = xp_yukle()
    puan = data.get(str(interaction.user.id), 0)
    await interaction.response.send_message(f"📊 Mevcut mesaj sayın (XP): {puan}")

@bot.tree.command(name="ban", description="Kullanıcıyı yasaklar.")
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.ban(reason=sebep)
    await log_gonder(interaction.guild, "Ban İşlemi", f"{member.mention} yasaklandı.\nSebep: {sebep}\nYapan: {interaction.user.name}")
    await interaction.response.send_message(f"🔨 {member.name} banlandı.")

@bot.tree.command(name="kick", description="Kullanıcıyı atar.")
async def kick(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.kick(reason=sebep)
    await log_gonder(interaction.guild, "Kick İşlemi", f"{member.mention} atıldı.\nSebep: {sebep}")
    await interaction.response.send_message(f"👢 {member.name} atıldı.")

@bot.tree.command(name="sustur", description="Kullanıcıyı susturur.")
async def sustur(interaction: discord.Interaction, member: discord.Member, dakika: int):
    await member.timeout(datetime.timedelta(minutes=dakika))
    await log_gonder(interaction.guild, "Susturma", f"{member.mention} {dakika} dakika susturuldu.")
    await interaction.response.send_message(f"🤐 {member.name} susturuldu.")

@bot.tree.command(name="temizle", description="Mesaj siler.")
async def temizle(interaction: discord.Interaction, miktar: int):
    await interaction.channel.purge(limit=miktar)
    await interaction.response.send_message(f"🧹 {miktar} mesaj silindi.", ephemeral=True)
    await log_gonder(interaction.guild, "Temizleme", f"{interaction.channel.mention} kanalında {miktar} mesaj silindi.")

# --- HOŞ GELDİN ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="╭・・Hoş Geldin", description=f"┆  Kullanıcı: {member.mention}\n┆  Üye Sayısı: {member.guild.member_count}\n┆  Sohbete katılmayı unutma!\n╰・・OwO Trades #AÇILIŞ", color=0x2ecc71)
        await channel.send(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
