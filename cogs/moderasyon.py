import discord
from discord.ext import commands
from discord import app_commands
import datetime
import json
import os

class Moderasyon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.KUFUR_LISTESI = ["sik", "am", "got", "yarak", "oç", "piç"]
        self.VIP_ROLE_ID = 1526638053798445156
        self.LOG_CHANNEL_ID = 1526664676425994260
        self.WARNINGS_FILE = "warnings.json"

    # --- YARDIMCI FONKSİYONLAR ---
    def uyarilari_yukle(self):
        if not os.path.exists(self.WARNINGS_FILE):
            return {}
        try:
            with open(self.WARNINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def uyarilari_kaydet(self, data):
        with open(self.WARNINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    async def log_gonder(self, guild, embed):
        channel = guild.get_channel(self.LOG_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

    # --- KÜFÜR ENGELLEYİCİ SİSTEM ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if any(role.id == self.VIP_ROLE_ID for role in message.author.roles):
            return
        
        content = message.content.lower().replace(" ", "")
        if any(kufur in content for kufur in self.KUFUR_LISTESI):
            await message.delete()
            
            # Üyeye sadece kendisinin göreceği gizli bir uyarı gönder (Ephemral mesaj taklidi için on_message içinde dm atılabilir veya geçici silinen mesaj atılabilir)
            uyari_msg = await message.channel.send(f"⚠️ {message.author.mention}, kelimelerine dikkat etmelisin! Bu mesaj 3 saniye içinde silinecektir.", delete_after=3)
            
            # Yetkili Logu
            embed = discord.Embed(title="🚨 Küfür Engellendi", color=0xff4757)
            embed.add_field(name="Kullanıcı", value=f"{message.author.mention} (`{message.author.id}`)", inline=True)
            embed.add_field(name="Mesaj İçeriği", value=f"||{message.content}||", inline=False)
            embed.set_timestamp()
            await self.log_gonder(message.guild, embed)

    # --- BAN KOMUTLARI ---
    @app_commands.command(name="ban", description="Kullanıcıyı sunucudan kalıcı olarak yasaklar.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ Kendini banlayamazsın!", ephemeral=True)
            return

        await member.ban(reason=sebep)
        await interaction.response.send_message(f"🔨 **{member.name}** başarıyla sunucudan uzaklaştırıldı.", ephemeral=True)

        embed = discord.Embed(title="🔨 Kullanıcı Banlandı", color=0xff4757)
        embed.add_field(name="Yasaklanan", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_timestamp()
        await self.log_gonder(interaction.guild, embed)

    @app_commands.command(name="unban", description="Kullanıcının yasağını ID kullanarak kaldırır.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str, sebep: str = "Belirtilmedi"):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=sebep)
            await interaction.response.send_message(f"🔓 **{user.name}** yasağı başarıyla kaldırıldı.", ephemeral=True)

            embed = discord.Embed(title="🔓 Ban Kaldırıldı", color=0x2ed573)
            embed.add_field(name="Yasağı Kaldırılan", value=f"{user.name} (`{user.id}`)", inline=True)
            embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
            embed.add_field(name="Sebep", value=sebep, inline=False)
            embed.set_timestamp()
            await self.log_gonder(interaction.guild, embed)
        except discord.NotFound:
            await interaction.response.send_message("❌ Belirtilen ID'ye sahip bir yasaklama bulunamadı.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Lütfen geçerli bir sayısal kullanıcı ID'si girin.", ephemeral=True)

    # --- KICK KOMUTU ---
    @app_commands.command(name="kick", description="Kullanıcıyı sunucudan atar.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ Kendini atamazsın!", ephemeral=True)
            return

        await member.kick(reason=sebep)
        await interaction.response.send_message(f"👢 **{member.name}** sunucudan atıldı.", ephemeral=True)

        embed = discord.Embed(title="👢 Kullanıcı Atıldı", color=0xffa502)
        embed.add_field(name="Atılan Üye", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_timestamp()
        await self.log_gonder(interaction.guild, embed)

    # --- TIMEOUT (MUTE) SYSTEM ---
    @app_commands.command(name="mute", description="Kullanıcıyı belirli bir süre susturur (Timeout).")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, dakika: int, sebep: str = "Belirtilmedi"):
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ Kendini susturamazsın!", ephemeral=True)
            return

        sure = datetime.timedelta(minutes=dakika)
        await member.timeout(sure, reason=sebep)
        await interaction.response.send_message(f"🤐 **{member.name}**, **{dakika}** dakika boyunca susturuldu.", ephemeral=True)

        embed = discord.Embed(title="🤐 Kullanıcı Susturuldu", color=0xff7f50)
        embed.add_field(name="Susturulan", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Süre", value=f"{dakika} Dakika", inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_timestamp()
        await self.log_gonder(interaction.guild, embed)

    @app_commands.command(name="unmute", description="Kullanıcının susturmasını kaldırır.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, sebep: str = "Belirtilmedi"):
        await member.timeout(None, reason=sebep)
        await interaction.response.send_message(f"🔊 **{member.name}** susturması kaldırıldı.", ephemeral=True)

        embed = discord.Embed(title="🔊 Susturma Kaldırıldı", color=0x2ed573)
        embed.add_field(name="Susturması Açılan", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_timestamp()
        await self.log_gonder(interaction.guild, embed)

    # --- UYARI (WARN) SYSTEM ---
    @app_commands.command(name="uyar", description="Kullanıcıya resmi uyarı ekler.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def uyar(self, interaction: discord.Interaction, member: discord.Member, sebep: str):
        if member.bot:
            await interaction.response.send_message("❌ Botları uyaramazsın!", ephemeral=True)
            return

        data = self.uyarilari_yukle()
        uid = str(member.id)
        
        if uid not in data:
            data[uid] = []
        
        uyari_detay = {
            "yetkili": interaction.user.name,
            "sebep": sebep,
            "tarih": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        data[uid].append(uyari_detay)
        self.uyarilari_kaydet(data)

        await interaction.response.send_message(f"⚠️ {member.mention} başarıyla uyarıldı. Toplam Uyarı: **{len(data[uid])}**", ephemeral=True)

        # Log Gönderimi
        embed = discord.Embed(title="⚠️ Yeni Uyarı", color=0xffa502)
        embed.add_field(name="Uyarılan Üye", value=f"{member.mention} (`{member.id}`)", inline=True)
        embed.add_field(name="Toplam Uyarı", value=f"**{len(data[uid])}**", inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.add_field(name="Sebep", value=sebep, inline=False)
        embed.set_timestamp()
        await self.log_gonder(interaction.guild, embed)

    @app_commands.command(name="uyarilar", description="Bir kullanıcının geçmiş uyarılarını listeler.")
    async def uyarilar(self, interaction: discord.Interaction, member: discord.Member):
        data = self.uyarilari_yukle()
        uid = str(member.id)

        if uid not in data or len(data[uid]) == 0:
            await interaction.response.send_message(f"ℹ️ {member.mention} kullanıcısının hiç uyarısı bulunmuyor.", ephemeral=True)
            return

        embed = discord.Embed(title=f"📋 {member.name} - Uyarı Geçmişi", color=0x3498db)
        for i, uyari in enumerate(data[uid], 1):
            embed.add_field(
                name=f"Uyarı #{i}",
                value=f"**Yetkili:** {uyari['yetkili']}\n**Sebep:** {uyari['sebep']}\n**Tarih:** {uyari['tarih']}",
                inline=False
            )
        embed.set_footer(text=f"Toplam Uyarı Sayısı: {len(data[uid])}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="uyari-sil", description="Kullanıcının tüm uyarı geçmişini temizler.")
    @app_commands.checks.has_permissions(administrator=True)
    async def uyari_sil(self, interaction: discord.Interaction, member: discord.Member):
        data = self.uyarilari_yukle()
        uid = str(member.id)

        if uid in data:
            data.pop(uid)
            self.uyarilari_kaydet(data)
            await interaction.response.send_message(f"✅ {member.mention} kullanıcısının tüm uyarıları sıfırlandı.", ephemeral=True)
            
            embed = discord.Embed(title="🧹 Uyarılar Sıfırlandı", color=0x2ed573)
            embed.add_field(name="Üye", value=member.mention, inline=True)
            embed.add_field(name="Sıfırlayan Yetkili", value=interaction.user.mention, inline=True)
            embed.set_timestamp()
            await self.log_gonder(interaction.guild, embed)
        else:
            await interaction.response.send_message("❌ Bu kullanıcının zaten aktif uyarısı bulunmuyor.", ephemeral=True)

    # --- TEMİZLE (PRUNE) KOMUTU ---
    @app_commands.command(name="temizle", description="Belirtilen miktarda mesajı siler.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def temizle(self, interaction: discord.Interaction, miktar: int):
        if miktar < 1 or miktar > 100:
            await interaction.response.send_message("❌ Lütfen 1 ile 100 arasında bir sayı girin.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True) # Silme işlemi uzun sürebileceği için etkileşimi açık tutuyoruz
        silinen = await interaction.channel.purge(limit=miktar)
        await interaction.followup.send(f"🧹 **{len(silinen)}** adet mesaj başarıyla temizlendi.", ephemeral=True)

        embed = discord.Embed(title="🧹 Kanal Temizlendi", color=0x54a0ff)
        embed.add_field(name="Kanal", value=interaction.channel.mention, inline=True)
        embed.add_field(name="Temizlenen Mesaj", value=f"**{len(silinen)}**", inline=True)
        embed.add_field(name="Yetkili", value=interaction.user.mention, inline=True)
        embed.set_timestamp()
        await self.log_gonder(interaction.guild, embed)

    # --- OTOMATİK HATA YAKALAYICI (KULLANICI BİLGİLENDİRME) ---
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ **Dur orada!** Bu komutu kullanmak için gerekli yetkilere sahip değilsin.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Bir sistem hatası meydana geldi:\n`{error}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderasyon(bot))
