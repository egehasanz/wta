import discord
from discord.ext import commands
import json
import os
import datetime

# --- AYARLAR ---
LOG_CHANNEL_ID = 1526664676425994260
MUAF_ROL_ID = 1526638053798445156

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# --- KOMUTLAR ---

# 1. Moderasyon & Yönetim
@bot.command()
async def ban(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.ban(reason=sebep)
    await ctx.send(f"🔨 {member.name} sunucudan uçuruldu.")

@bot.command()
async def kick(ctx, member: discord.Member, *, sebep="Belirtilmedi"):
    await member.kick(reason=sebep)
    await ctx.send(f"👢 {member.name} tekmelendi.")

@bot.command()
async def sustur(ctx, member: discord.Member, dakika: int):
    await member.timeout(datetime.timedelta(minutes=dakika))
    await ctx.send(f"🤐 {member.name} {dakika} dakika susturuldu.")

@bot.command()
async def temizle(ctx, miktar: int):
    await ctx.channel.purge(limit=miktar + 1)
    await ctx.send(f"🧹 {miktar} mesaj silindi.", delete_after=3)

@bot.command()
async def lockdown(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kanal kilitlendi.")

@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kanal kilidi açıldı.")

# 2. Bilgi & Profil
@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name} - Avatar", color=0x3498db)
    embed.set_image(url=member.avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def rolbilgi(ctx, role: discord.Role):
    embed = discord.Embed(title=f"Role: {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id)
    embed.add_field(name="Üye Sayısı", value=len(role.members))
    embed.add_field(name="Oluşturulma", value=role.created_at.strftime("%d/%m/%Y"))
    await ctx.send(embed=embed)

@bot.command()
async def sunucubilgi(ctx):
    e = discord.Embed(title=f"📊 {ctx.guild.name}", color=0x00ff00)
    e.add_field(name="Üyeler", value=ctx.guild.member_count)
    e.add_field(name="Roller", value=len(ctx.guild.roles))
    e.add_field(name="Kanal", value=len(ctx.guild.channels))
    await ctx.send(embed=e)

# 3. İletişim & Eğlence
@bot.command()
async def duyuru(ctx, *, mesaj):
    embed = discord.Embed(title="📢 Yeni Duyuru", description=mesaj, color=0xf1c40f)
    embed.set_footer(text=f"Gönderen: {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Gecikme: {round(bot.latency * 1000)}ms")

# 4. Gelişmiş Yardım Menüsü
@bot.command(name="yardim")
async def yardim(ctx):
    e = discord.Embed(title="🛡️ WTA Security - Komuta Merkezi", color=0x9b59b6)
    e.add_field(name="🔨 Moderasyon", value="`.ban`, `.kick`, `.sustur`, `.temizle`, `.lockdown`, `.unlock`", inline=False)
    e.add_field(name="👤 Profil & Bilgi", value="`.userinfo`, `.avatar`, `.rolbilgi`, `.sunucubilgi`", inline=False)
    e.add_field(name="📢 Genel", value="`.duyuru`, `.ping`", inline=False)
    e.set_thumbnail(url=bot.user.avatar.url)
    await ctx.send(embed=e)

bot.run(os.getenv("BOT_TOKEN"))
