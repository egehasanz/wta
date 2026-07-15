import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.KUFUR_LISTESI = ["sik", "am", "got", "yarak", "oç", "piç"]
        self.VIP_ROLE_ID = 1526638053798445156

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if any(role.id == self.VIP_ROLE_ID for role in message.author.roles):
            return
        
        content = message.content.lower().replace(" ", "")
        if any(kufur in content for kufur in self.KUFUR_LISTESI):
            await message.delete()

    @app_commands.command(name="ban", description="Kullanıcıyı yasaklar.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
        await member.ban(reason=sebep)
        await interaction.response.send_message(f"🔨 {member.name} yasaklandı.")

    @app_commands.command(name="mute", description="Kullanıcıyı susturur.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, dakika: int):
        await member.timeout(datetime.timedelta(minutes=dakika))
        await interaction.response.send_message(f"🤐 {member.name} {dakika} dakika susturuldu.")

    @app_commands.command(name="unmute", description="Susturmayı kaldırır.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(f"🔊 {member.name} susturması kaldırıldı.")

    # İŞTE BURADA:
    @app_commands.command(name="temizle", description="Belirtilen miktarda mesajı siler.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def temizle(self, interaction: discord.Interaction, miktar: int):
        if miktar < 1 or miktar > 100:
            await interaction.response.send_message("Lütfen 1 ile 100 arasında bir sayı girin.", ephemeral=True)
            return
        silinen = await interaction.channel.purge(limit=miktar)
        await interaction.response.send_message(f"🧹 {len(silinen)} mesaj silindi.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderasyon(bot))