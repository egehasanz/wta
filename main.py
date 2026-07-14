import discord
from discord.ext import commands
import json
import os

# Ayarlar
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = 1507395734163689583
DATA_FILE = "authorized_users.json"

# Yetkili verisi yükleme
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([OWNER_ID], f) # Bot sahibini otomatik ekle

def load_authorized():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_authorized(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

def is_authorized(ctx):
    users = load_authorized()
    return ctx.author.id in users

@bot.event
async def on_ready():
    print(f"{bot.user} başarıyla başlatıldı.")

@bot.command()
async def yetkiekle(ctx, member: discord.Member):
    if ctx.author.id != OWNER_ID: return
    users = load_authorized()
    if member.id not in users:
        users.append(member.id)
        save_authorized(users)
        await ctx.send(f"{member.name} artık yetkili.")
    else:
        await ctx.send("Kullanıcı zaten yetkili.")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} yasaklandı.")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="Sebep yok"):
    if not is_authorized(ctx): return
    await member.kick(reason=reason)
    await ctx.send(f"{member.name} atıldı.")

@bot.command()
async def temizle(ctx, amount: int):
    if not is_authorized(ctx): return
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} mesaj silindi.", delete_after=3)

@bot.command()
async def rolver(ctx, member: discord.Member, role: discord.Role):
    if not is_authorized(ctx): return
    await member.add_roles(role)
    await ctx.send(f"{member.name} kişisine {role.name} rolü verildi.")

@bot.command()
async def rolal(ctx, member: discord.Member, role: discord.Role):
    if not is_authorized(ctx): return
    await member.remove_roles(role)
    await ctx.send(f"{member.name} kişisinden {role.name} rolü alındı.")

@bot.command()
async def sunucubilgi(ctx):
    if not is_authorized(ctx): return
    embed = discord.Embed(title="Sunucu Bilgileri", color=discord.Color.blue())
    embed.add_field(name="Üye Sayısı", value=ctx.guild.member_count)
    embed.add_field(name="Kuruluş", value=ctx.guild.created_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)

@bot.command()
async def yardım(ctx):
    await ctx.send("Komutlar: .ban, .kick, .temizle, .rolver, .rolal, .sunucubilgi, .yetkiekle, .yardım")

bot.run(TOKEN)
