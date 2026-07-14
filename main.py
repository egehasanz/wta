import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os

# --- AYARLAR ---
LOG_CHANNEL_ID = 1526664676425994260
WELCOME_CHANNEL_ID = 1526706539614699591

# --- BOT BAŞLATMA (Intents burada tanımlandı) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- LOG SİSTEMİ ---
async def log_gonder(guild, baslik, detay):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=f"🛡️ {baslik}", description=detay, color=discord.Color.red())
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} - WTA Security Aktif ve Slash Komutlar Senkronize Edildi!")

# --- HOŞ GELDİN / GİDİŞ ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="╭・・Hoş Geldin",
            description=f"┆  Kullanıcı: {member.mention}\n┆  Üye Sayısı: {member.guild.member_count}\n┆  Sohbete katılmayı unutma!\n╰・・OwO Trades #AÇILIŞ",
            color=0x2ecc71
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="╭・・Güle Güle",
            description=f"┆  Kullanıcı: {member.name}\n┆  Aramızdan ayrıldı.\n╰・・",
            color=0xe74c3c
        )
        await channel.send(embed=embed)

# --- SLASH KOMUTLARI ---
@bot.tree.command(name="ban", description="Kullanıcıyı yasaklar.")
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.ban(reason=sebep)
    await log_gonder(interaction.guild, "Ban", f"{member.mention} yasaklandı. Sebep: {sebep}")
    await interaction.response.send_message(f"🔨 {member.name} banlandı.")

@bot.tree.command(name="kick", description="Kullanıcıyı atar.")
async def kick(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.kick(reason=sebep)
    await log_gonder(interaction.guild, "Kick", f"{member.mention} atıldı. Sebep: {sebep}")
    await interaction.response.send_message(f"👢 {member.name} atıldı.")

@bot.tree.command(name="sustur", description="Kullanıcıyı susturur.")
async def sustur(interaction: discord.Interaction, member: discord.Member, dakika: int):
    await member.timeout(datetime.timedelta(minutes=dakika))
    await interaction.response.send_message(f"🤐 {member.name} {dakika} dakika susturuldu.")

@bot.tree.command(name="temizle", description="Mesajları siler.")
async def temizle(interaction: discord.Interaction, miktar: int):
    await interaction.channel.purge(limit=miktar)
    await interaction.response.send_message(f"🧹 {miktar} mesaj silindi.", ephemeral=True)

@bot.tree.command(name="lockdown", description="Kanalı kilitler.")
async def lockdown(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Kanal kilitlendi.")

@bot.tree.command(name="unlock", description="Kilidi açar.")
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 Kanal kilidi açıldı.")

@bot.tree.command(name="userinfo", description="Kullanıcı bilgisi.")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"👤 {member.name} Bilgileri", color=0x3498db)
    embed.add_field(name="Katılım", value=member.joined_at.strftime("%d/%m/%Y"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="yardim", description="Yardım menüsü.")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Paneli", color=0x9b59b6)
    embed.add_field(name="🔨 Moderasyon", value="/ban, /kick, /sustur, /temizle", inline=False)
    embed.add_field(name="🔒 Güvenlik", value="/lockdown, /unlock, /userinfo", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
