import discord
from discord.ext import commands
import json
import os
import datetime

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
DATA_FILE = "authorized_users.json"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİ YÖNETİMİ ---
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([OWNER_ID], f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def is_authorized(ctx):
    return ctx.author.id in load_data() or ctx.author.id == OWNER_ID

# --- EVENTLER ---
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="OwO Trades #AÇILIŞ")
    await bot.change_presence(activity=activity)
    print(f"{bot.user} aktif!")

@bot.event
async def on_message(message):
    if message.author.bot: return
    # Basit Reklam Engelleme
    if "discord.gg/" in message.content:
        await message.delete()
        await message.channel.send(f"{message.author.mention} Reklam yasak!")
    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.command()
async def yetkiekle(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID: return
    data = load_data()
    if member.id not in data:
        data.append(member.id)
        with open(DATA_FILE, "w") as f: json.dump(data, f)
        await ctx.send(f"{member.name} yetkilendirildi.")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} banlandı.")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    await member.kick(reason=reason)
    await ctx.send(f"{member.name} atıldı.")

@bot.command()
async def mute(ctx, member: discord.Member, duration: int, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
    await member.timeout(until, reason=reason)
    await ctx.send(f"{member.name} {duration} dakika susturuldu.")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if not is_authorized(ctx): return
    await member.timeout(None)
    await ctx.send(f"{member.name} susturması kaldırıldı.")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    await ctx.send(f"{member.name} uyarıldı: {reason}")

@bot.command()
async def temizle(ctx, amount: int):
    if not is_authorized(ctx): return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} mesaj silindi.", delete_after=3)

@bot.command()
async def rolver(ctx, member: discord.Member, role: discord.Role):
    if not is_authorized(ctx): return
    await member.add_roles(role)
    await ctx.send(f"{role.name} rolü verildi.")

@bot.command()
async def rolal(ctx, member: discord.Member, role: discord.Role):
    if not is_authorized(ctx): return
    await member.remove_roles(role)
    await ctx.send(f"{role.name} rolü alındı.")

@bot.command()
async def sunucubilgi(ctx):
    if not is_authorized(ctx): return
    embed = discord.Embed(title="Sunucu Bilgisi", color=discord.Color.green())
    embed.add_field(name="Üye Sayısı", value=ctx.guild.member_count)
    await ctx.send(embed=embed)

@bot.command()
async def yardım(ctx):
    await ctx.send("Komutlar: .ban, .kick, .mute, .unmute, .warn, .temizle, .rolver, .rolal, .sunucubilgi, .yetkiekle")

bot.run(os.getenv("BOT_TOKEN"))
