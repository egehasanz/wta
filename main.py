import discord
from discord.ext import commands
import json
import os
import datetime
import asyncio

# --- AYARLAR ---
OWNER_ID = 1507395734163689583
DATA_FILE = "authorized_users.json"
WARN_FILE = "warnings.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

# --- VERİ YÖNETİMİ ---
def load_json(filename):
    if not os.path.exists(filename): return {} if filename == WARN_FILE else [OWNER_ID]
    with open(filename, "r") as f: return json.load(f)

def save_json(filename, data):
    with open(filename, "w") as f: json.dump(data, f, indent=4)

# --- KOMUTLAR (Efektli) ---

@bot.command()
async def mute(ctx, member: discord.Member, minutes: int, *, reason="Sebep yok"):
    # 1. Aşama: Animasyonlu Başlangıç
    msg = await ctx.send(f"⏳ **{member.name}** susturuluyor...")
    await asyncio.sleep(1)
    
    try:
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        # 2. Aşama: Başarılı Güncelleme (Animasyon etkisi)
        await msg.edit(content=f"🤐 **{member.name}** başarıyla susturuldu! (Süre: {minutes}dk)")
    except Exception as e:
        await msg.edit(content=f"❌ **{member.name}** susturulamadı! Yetkilerimi kontrol et.")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Sebep yok"):
    warns = load_json(WARN_FILE)
    m_id = str(member.id)
    warns[m_id] = warns.get(m_id, 0) + 1
    save_json(WARN_FILE, warns)
    
    # Animasyonlu Uyarı Mesajı
    msg = await ctx.send("⚠️ İşleniyor...")
    await asyncio.sleep(0.5)
    await msg.edit(content=f"⚠️ **{member.name}** uyarıldı! (Toplam Uyarı: {warns[m_id]})")

@bot.command()
async def temizle(ctx, amount: int):
    # Yazı yazma efekti
    msg = await ctx.send(f"🧹 {amount} mesaj temizleniyor...")
    await asyncio.sleep(1)
    await ctx.channel.purge(limit=amount + 2) # msg + komut mesajı
    # Silindikten sonra son bir mesaj
    final_msg = await ctx.send(f"✅ {amount} mesaj başarıyla süpürüldü!")
    await asyncio.sleep(2)
    await final_msg.delete()

@bot.command()
async def sunucubilgi(ctx):
    # Embed ile şık sunum
    msg = await ctx.send("📊 Bilgiler alınıyor...")
    await asyncio.sleep(0.5)
    embed = discord.Embed(title="📊 Sunucu İstatistikleri", color=discord.Color.gold())
    embed.add_field(name="Üye Sayısı", value=ctx.guild.member_count, inline=True)
    embed.add_field(name="Kuruluş", value=ctx.guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await msg.edit(content="İşte güncel sunucu bilgileri:", embed=embed)

# (Diğer komutlar aynı yapıda...)

bot.run(os.getenv("BOT_TOKEN"))
