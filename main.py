import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os

# --- AYARLAR (ID'lerini buraya göre kontrol et) ---
LOG_CHANNEL_ID = 1526664676425994260
TICKET_CATEGORY_ID = 1526969198365114448
VIP_ROLE_ID = 1526638053798445156
KUFUR_LISTESI = ["sik", "am", "got", "yarak", "oç", "piç"] 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- YARDIMCI SİSTEMLER ---
async def log_gonder(guild, baslik, detay):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title=f"🛡️ {baslik}", description=detay, color=discord.Color.red())
        await channel.send(embed=embed)

# --- TICKET KONTROL (KAPATMA BUTONU) ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Talebi Kapat", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Yetkili kontrolü de eklenebilir ama şu an basan kapatır
        await interaction.response.send_message("⚠️ Destek talebi kapatılıyor, kanal 5 saniye içinde silinecek...")
        await log_gonder(interaction.guild, "Ticket Kapatıldı", f"Kanal: {interaction.channel.name}\nKapatan: {interaction.user.mention}")
        await interaction.channel.delete()

# --- TICKET PANEL (AÇMA BUTONU) ---
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Destek Talebi Oluştur", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        
        # Kullanıcının zaten bir bileti var mı kontrolü (İsteğe bağlı eklenebilir)
        
        # Kanal izinleri: Sadece açan kişi ve bot görsün
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        # Biletin içine giden karşılama mesajı
        embed = discord.Embed(
            title="👋 Destek Talebine Hoş Geldin!",
            description=(
                f"Merhaba {interaction.user.mention},\n\n"
                "Destek talebin başarıyla oluşturuldu. Yetkililerimiz en kısa sürede seninle ilgilenecek.\n"
                "Lütfen sorununuzu detaylıca yazın ve yetkilileri bekleyin.\n\n"
                "**Bilet işlemleri bittiğinde aşağıdaki butonu kullanabilirsin.**"
            ),
            color=0x2ecc71
        )
        embed.set_footer(text="WTA Security Ticket Sistemi")
        
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Destek talebin oluşturuldu: {channel.mention}", ephemeral=True)
        await log_gonder(guild, "Yeni Ticket", f"Açan: {interaction.user.mention}\nKanal: {channel.mention}")

# --- EVENTS ---
@bot.event
async def on_ready():
    # Butonların bot kapanıp açılınca çalışması için add_view şart
    bot.add_view(TicketPanelView())
    bot.add_view(CloseTicketView())
    await bot.tree.sync()
    print(f"🚀 {bot.user} Aktif! Ticket ve Küfür Engelleyici hazır.")

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # VIP Muafiyet Kontrolü
    is_vip = any(role.id == VIP_ROLE_ID for role in message.author.roles)
    
    if not is_vip:
        # Küfür kontrolü (Boşlukları siler, kelime içinde geçerse yakalar: sikxxcxx)
        content = message.content.lower().replace(" ", "")
        if any(kufur in content for kufur in KUFUR_LISTESI):
            await message.delete()
            # Opsiyonel: Uyarı mesajı
            await message.channel.send(f"⚠️ {message.author.mention}, kelime tercihlerine dikkat etmelisin!", delete_after=3)
            return

    await bot.process_commands(message)

# --- KOMUTLAR ---
@bot.tree.command(name="ticket", description="Bilet açma panelini gönderir (Herkes kullanabilir).")
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📩 Destek Talebi",
        description=(
            "Bir sorununuz mu var? Yardıma mı ihtiyacınız var?\n"
            "Aşağıdaki butona tıklayarak sadece sizin ve yetkililerin görebileceği bir destek kanalı açabilirsiniz."
        ),
        color=0x3498db
    )
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    # Herkesin kullanabilmesi için permission check eklemedim
    await interaction.response.send_message("Destek paneli gönderildi.", ephemeral=True)
    await interaction.channel.send(embed=embed, view=TicketPanelView())

@bot.tree.command(name="ban", description="Kullanıcıyı yasaklar.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
    await member.ban(reason=sebep)
    await interaction.response.send_message(f"🔨 {member.name} yasaklandı. Sebep: {sebep}")
    await log_gonder(interaction.guild, "Ban Atıldı", f"Hedef: {member.mention}\nYapan: {interaction.user.mention}")

@bot.tree.command(name="mute", description="Kullanıcıyı susturur.")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, dakika: int):
    await member.timeout(datetime.timedelta(minutes=dakika))
    await interaction.response.send_message(f"🤐 {member.name} {dakika} dakika susturuldu.")
    await log_gonder(interaction.guild, "Mute Atıldı", f"Hedef: {member.mention}\nSüre: {dakika} dk")

bot.run(os.getenv("BOT_TOKEN"))
