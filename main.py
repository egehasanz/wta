import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json
import os

# --- AYARLAR ---
LOG_CHANNEL_ID = 1526664676425994260
WELCOME_CHANNEL_ID = 1526706539614699591
TICKET_CATEGORY_ID = 1526969198365114448
KUFUR_FILE = "kufurler.txt"
XP_FILE = "xp_data.json"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- YARDIMCI SİSTEMLER ---
def kufurleri_yukle():
    if not os.path.exists(KUFUR_FILE): return []
    with open(KUFUR_FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

def xp_yukle():
    if not os.path.exists(XP_FILE): return {}
    with open(XP_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def xp_kaydet(data):
    with open(XP_FILE, "w") as f: json.dump(data, f, indent=4)

async def log_gonder(guild, baslik, detay):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=f"🛡️ {baslik}", description=detay, color=discord.Color.red())
        await channel.send(embed=embed)

# --- EVENTLER ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("WTA Security - Tüm sistemler (Moderasyon + Ticket + XP + Koruma) aktif!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # 1. Küfür Kontrolü
    kufurler = kufurleri_yukle()
    if any(kelime in message.content.lower() for kelime in kufurler):
        await message.delete()
        await log_gonder(message.guild, "Küfür Engellendi", f"{message.author.mention} mesajı silindi.")
        return

    # 2. XP Sistemi
    data = xp_yukle()
    uid = str(message.author.id)
    data[uid] = data.get(uid, 0) + 1
    xp_kaydet(data)
    
    if data[uid] % 50 == 0:
        await message.channel.send(f"🎉 **{message.author.name}**, Level {data[uid] // 50} oldun!")

    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.tree.command(name="ban", description="Kullanıcıyı yasaklar.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.ban(reason=sebep)
    await log_gonder(interaction.guild, "Ban", f"{member.mention} yasaklandı. Sebep: {sebep}")
    await interaction.response.send_message(f"🔨 {member.name} yasaklandı.")

@bot.tree.command(name="unban", description="Kullanıcının yasağını kaldırır.")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(int(user_id))
    await interaction.guild.unban(user)
    await log_gonder(interaction.guild, "Unban", f"{user.name} yasağı kaldırıldı.")
    await interaction.response.send_message(f"🔓 {user.name} yasağı kaldırıldı.")

@bot.tree.command(name="mute", description="Kullanıcıyı susturur.")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, dakika: int):
    await member.timeout(datetime.timedelta(minutes=dakika))
    await log_gonder(interaction.guild, "Mute", f"{member.mention} {dakika} dk susturuldu.")
    await interaction.response.send_message(f"🤐 {member.name} susturuldu.")

@bot.tree.command(name="unmute", description="Susturmayı kaldırır.")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await log_gonder(interaction.guild, "Unmute", f"{member.mention} susturması kaldırıldı.")
    await interaction.response.send_message(f"🔊 {member.name} susturması kaldırıldı.")

@bot.tree.command(name="ticket", description="Destek talebi açar.")
async def ticket(interaction: discord.Interaction):
    category = interaction.guild.get_channel(TICKET_CATEGORY_ID)
    channel = await interaction.guild.create_text_channel(
        name=f"destek-{interaction.user.name}",
        category=category,
        overwrites={
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
    )
    await interaction.response.send_message(f"✅ Ticket açıldı: {channel.mention}", ephemeral=True)

@bot.tree.command(name="yardim", description="Komut menüsü.")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Merkezi", color=0x3498db)
    embed.add_field(name="🔨 Moderasyon", value="/ban, /unban, /mute, /unmute, /kick, /temizle", inline=False)
    embed.add_field(name="🔒 Ticket & XP", value="/ticket, /xp", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
