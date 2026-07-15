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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} - WTA Security Tüm Sistemler (Log+XP) Aktif!")

# --- MESAJ VE XP SİSTEMİ ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    data = xp_yukle()
    user_id = str(message.author.id)
    yeni_puan = data.get(user_id, 0) + 1
    data[user_id] = yeni_puan
    xp_kaydet(data)
    
    if yeni_puan % 50 == 0:
        yeni_level = yeni_puan // 50
        embed = discord.Embed(title="🎉 SEVİYE ATLADIN!", description=f"Tebrikler {message.author.mention}, **Level {yeni_level}** oldun!", color=0xf1c40f)
        await message.channel.send(embed=embed)
    
    await bot.process_commands(message)

# --- GİRİŞ / ÇIKIŞ ---
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="╭・・Hoş Geldin", description=f"┆  Kullanıcı: {member.mention}\n┆  Üye Sayısı: {member.guild.member_count}\n┆  Sohbete katılmayı unutma!\n╰・・OwO Trades #AÇILIŞ", color=0x2ecc71)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="╭・・Güle Güle", description=f"┆  Kullanıcı: {member.name}\n┆  Aramızdan ayrıldı.\n╰・・", color=0xe74c3c)
        await channel.send(embed=embed)

# --- SLASH KOMUTLARI ---
@bot.tree.command(name="xp", description="Seviyeni gösterir.")
async def xp(interaction: discord.Interaction):
    data = xp_yukle()
    puan = data.get(str(interaction.user.id), 0)
    level = puan // 50
    await interaction.response.send_message(f"📊 **{interaction.user.name}**\nLevel: {level}\nToplam XP: {puan}")

@bot.tree.command(name="ban", description="Kullanıcıyı yasaklar.")
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.ban(reason=sebep)
    await log_gonder(interaction.guild, "Ban İşlemi", f"{member.mention} yasaklandı. Sebep: {sebep}")
    await interaction.response.send_message(f"🔨 {member.name} banlandı.")

@bot.tree.command(name="kick", description="Kullanıcıyı atar.")
async def kick(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.kick(reason=sebep)
    await log_gonder(interaction.guild, "Kick İşlemi", f"{member.mention} atıldı. Sebep: {sebep}")
    await interaction.response.send_message(f"👢 {member.name} atıldı.")

@bot.tree.command(name="sustur", description="Kullanıcıyı susturur.")
async def sustur(interaction: discord.Interaction, member: discord.Member, dakika: int):
    await member.timeout(datetime.timedelta(minutes=dakika))
    await log_gonder(interaction.guild, "Susturma", f"{member.mention} {dakika} dk susturuldu.")
    await interaction.response.send_message(f"🤐 {member.name} susturuldu.")

@bot.tree.command(name="temizle", description="Mesajları siler.")
async def temizle(interaction: discord.Interaction, miktar: int):
    await interaction.channel.purge(limit=miktar)
    await interaction.response.send_message(f"🧹 {miktar} mesaj silindi.", ephemeral=True)
    await log_gonder(interaction.guild, "Temizleme", f"{interaction.channel.mention} kanalında {miktar} mesaj silindi.")

@bot.tree.command(name="yardim", description="Yardım menüsü.")
async def yardim(interaction: discord.Interaction):
    embed = discord.Embed(title="🛡️ WTA Security - Komut Paneli", color=0x9b59b6)
    embed.add_field(name="Moderasyon", value="/ban, /kick, /sustur, /temizle", inline=False)
    embed.add_field(name="Diğer", value="/xp", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("BOT_TOKEN"))
