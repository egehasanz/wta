import discord
from discord.ext import commands
from discord import app_commands
import io
import datetime

# --- TICKET MODAL (FORM) ---
class TicketModal(discord.ui.Modal, title='Destek Talebi Formu'):
    problem = discord.ui.TextInput(
        label='Sorununuz Nedir?',
        placeholder='Lütfen sorununuzu detaylıca buraya yazın...',
        style=discord.TextStyle.long,
        min_length=10,
    )
    urgency = discord.ui.TextInput(
        label='Aciliyet Durumu',
        placeholder='Düşük / Orta / Yüksek',
        max_length=10,
    )

    def __init__(self, category_id, role_id):
        super().__init__()
        self.category_id = category_id
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Mükerrer Kontrol
        for ch in guild.text_channels:
            if ch.name == f"ticket-{interaction.user.name.lower()}":
                await interaction.response.send_message("❌ Zaten aktif bir destek talebin bulunuyor!", ephemeral=True)
                return

        cat = guild.get_channel(self.category_id)
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            category=cat,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        # Karşılama Mesajı
        embed = discord.Embed(
            title="🎫 Yeni Destek Talebi",
            description=f"Selam {interaction.user.mention}, talebin başarıyla açıldı.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📝 Sorun", value=f"```{self.problem.value}```", inline=False)
        embed.add_field(name="🚨 Aciliyet", value=f"`{self.urgency.value}`", inline=True)
        embed.add_field(name="👤 Kullanıcı", value=interaction.user.mention, inline=True)
        embed.set_footer(text="Talebi kapatmak için aşağıdaki butonu kullanın.")
        
        await channel.send(content=f"<@&{self.role_id}>", embed=embed, view=TicketControls())
        await interaction.response.send_message(f"✅ Talebin oluşturuldu: {channel.mention}", ephemeral=True)

# --- TICKET KONTROLLERİ (KAPAT / LOG) ---
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Talebi Kapat", style=discord.ButtonStyle.red, custom_id="close_ticket", emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💾 Transkript alınıyor ve kanal siliniyor...")
        
        # Transkript Oluşturma
        messages = [message async for message in interaction.channel.history(limit=None, oldest_first=True)]
        transcript = ""
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            transcript += f"[{timestamp}] {msg.author.name}: {msg.content}\n"
        
        file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{interaction.channel.name}.txt")
        
        # Log Kanalına Gönder (Moderasyon modülündeki ID'yi kullanır)
        log_channel = interaction.guild.get_channel(1526664676425994260) 
        if log_channel:
            log_embed = discord.Embed(
                title="🔒 Ticket Kapatıldı",
                description=f"**Kanal:** {interaction.channel.name}\n**Kapatan:** {interaction.user.mention}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            await log_channel.send(embed=log_embed, file=file)

        await interaction.channel.delete()

# --- ANA PANEL ---
class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_ID = 1526969198365114448
        self.ROLE_ID = 1526638059880321256

    @app_commands.command(name="ticket", description="Profesyonel Destek Paneli oluşturur.")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 WTA Security | Destek Merkezi",
            description=(
                "Yardıma mı ihtiyacınız var?\n\n"
                "**1.** Aşağıdaki butona tıklayın.\n"
                "**2.** Açılan formu doldurun.\n"
                "**3.** Yetkililerimizin sizinle ilgilenmesini bekleyin."
            ),
            color=0x2b2d31
        )
        embed.set_image(url="https://i.imgur.com/8N4Y84m.png") # Buraya sunucuna özel bir banner koyabilirsin
        
        view = discord.ui.View(timeout=None)
        btn = discord.ui.Button(label="Destek Talebi Aç", style=discord.ButtonStyle.blurple, emoji="📩", custom_id="persistent_open")
        
        async def btn_callback(inter):
            await inter.response.send_modal(TicketModal(self.CATEGORY_ID, self.ROLE_ID))
        
        btn.callback = btn_callback
        view.add_item(btn)
        
        await interaction.response.send_message("Panel Kuruldu.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Ticket(bot))
