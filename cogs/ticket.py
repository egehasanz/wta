import discord
from discord.ext import commands
from discord import app_commands

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_ID = 1526969198365114448
        self.ROLE_ID = 1526638059880321256

    @app_commands.command(name="ticket", description="Destek paneli açar.")
    async def ticket(self, interaction: discord.Interaction):
        view = TicketPanelView(self.CATEGORY_ID, self.ROLE_ID)
        embed = discord.Embed(title="📩 Destek Merkezi", description="Butona basarak bilet aç.", color=0x3498db)
        await interaction.response.send_message(embed=embed, view=view)

class TicketPanelView(discord.ui.View):
    def __init__(self, cat_id, role_id):
        super().__init__(timeout=None)
        self.cat_id = cat_id
        self.role_id = role_id

    @discord.ui.button(label="📩 Destek Aç", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        for ch in interaction.guild.text_channels:
            if ch.name == f"ticket-{interaction.user.name.lower()}":
                await interaction.response.send_message("❌ Zaten açık bir biletin var!", ephemeral=True)
                return
        
        cat = interaction.guild.get_channel(self.cat_id)
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            category=cat,
            overwrites={interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
        )
        await channel.send(f"👋 Merhaba {interaction.user.mention}, <@&{self.role_id}> ilgilenecek.", view=CloseView())
        await interaction.response.send_message(f"✅ Biletin açıldı: {channel.mention}", ephemeral=True)

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Kapat", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

async def setup(bot):
    await bot.add_cog(Ticket(bot))