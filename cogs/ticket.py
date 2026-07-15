import discord
from discord.ext import commands
from discord import app_commands

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_ID = 1526969198365114448
        self.ROLE_ID = 1526638059880321256

    @app_commands.command(name="ticket", description="Destek paneli oluşturur.")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📩 WTA Security Destek Merkezi",
            description="Sorunlarını bildirmek veya yardım almak için aşağıdaki butona tıkla.",
            color=0x2b2d31
        )
        embed.set_footer(text="Yetkililer en kısa sürede seninle ilgilenecektir.")
        await interaction.response.send_message(embed=embed, view=TicketPanelView(self.CATEGORY_ID, self.ROLE_ID))

class TicketPanelView(discord.ui.View):
    def __init__(self, cat_id, role_id):
        super().__init__(timeout=None)
        self.cat_id = cat_id
        self.role_id = role_id

    @discord.ui.button(label="Destek Talebi Aç", style=discord.ButtonStyle.green, custom_id="open_ticket", emoji="📩")
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Mükerrer bilet kontrolü
        for ch in interaction.guild.text_channels:
            if ch.name == f"ticket-{interaction.user.name.lower()}":
                await interaction.response.send_message("❌ Zaten açık bir biletin var!", ephemeral=True)
                return
        
        cat = interaction.guild.get_channel(self.cat_id)
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            category=cat,
            overwrites={interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                        interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        )
        
        # Profesyonel Karşılama Embed'i
        embed = discord.Embed(
            title="🎫 Destek Talebi Oluşturuldu",
            description=f"Merhaba {interaction.user.mention},\n\nSorununu detaylıca açıklarsan <@&{self.role_id}> ekibimiz sana en kısa sürede yardımcı olacaktır.",
            color=0x00ff9d
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await channel.send(embed=embed, view=CloseView())
        await interaction.response.send_message(f"✅ Biletin oluşturuldu: {channel.mention}", ephemeral=True)

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Talebi Kapat", style=discord.ButtonStyle.red, custom_id="close_btn", emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Kanal siliniyor...")
        await interaction.channel.delete()

async def setup(bot):
    await bot.add_cog(Ticket(bot))
