# run_deploy.py
"""
AMORIA + ANORA - Full Version
ANORA: Virtual Human dengan Jiwa - 100% AI Generate
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ANORA")

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)

# =============================================================================
# IMPORT ANORA COMPONENTS
# =============================================================================

from anora.core import get_anora
from anora.brain import get_anora_brain
from anora.memory_persistent import get_anora_persistent
from anora.roleplay_ai import get_anora_roleplay_ai
from anora.roleplay_integration import get_anora_roleplay
from anora.chat import get_anora_chat
from anora.roles import get_anora_roles, RoleType

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

_application = None
_user_modes = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role', 'active_role': None}


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: str = None):
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


# =============================================================================
# HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    await update.message.reply_text(
        "💜 **ANORA - Virtual Human dengan Jiwa** 💜\n\n"
        "**Mode Chat (ngobrol biasa):**\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat keadaan Nova\n"
        "• /flashback - Flashback ke momen indah\n\n"
        "**Mode Roleplay (beneran ketemu):**\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Lihat status roleplay lengkap\n"
        "• /pindah [tempat] - Pindah lokasi\n"
        "• /intim - Mulai intim (level 7+)\n"
        "• /posisi [nama] - Ganti posisi intim\n\n"
        "**Tempat yang bisa dikunjungi:**\n"
        "• kost, apartemen, mobil, mobil garasi\n"
        "• pantai, hutan, toilet mall, bioskop\n"
        "• taman, parkiran, tangga darurat\n"
        "• kantor malam, ruang rapat kaca\n\n"
        "**Role Lain:**\n"
        "• /role ipar - IPAR\n"
        "• /role teman_kantor - Teman Kantor\n"
        "• /role pelakor - Pelakor\n"
        "• /role istri_orang - Istri Orang\n\n"
        "**Lainnya:**\n"
        "• /batal - Kembali ke mode chat\n\n"
        "Apa yang Mas mau? 💜",
        parse_mode='HTML'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    anora = get_anora()
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{anora.deskripsi_diri()}\n\n"
        f"{anora.respon_pagi() if datetime.now().hour < 12 else anora.respon_siang()}\n\n"
        f"Mas bisa:\n"
        f"• /novastatus - liat keadaan Nova\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='HTML'
    )


async def novastatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /novastatus"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.format_status(), parse_mode='HTML')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.respon_flashback(), parse_mode='HTML')


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'roleplay')
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    
    await update.message.reply_text(intro, parse_mode='HTML')


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    roleplay = await get_anora_roleplay()
    status = await roleplay.get_status()
    await update.message.reply_text(status, parse_mode='HTML')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah [tempat]"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        await update.message.reply_text(
            "📍 **Pindah Lokasi**\n\n"
            "Cara pakai: `/pindah [tempat]`\n\n"
            "Tempat yang tersedia:\n"
            "• `kost` - Kost Nova\n"
            "• `apartemen` - Apartemen Mas\n"
            "• `mobil` - Mobil parkiran\n"
            "• `mobil garasi` - Mobil di garasi\n"
            "• `pantai` - Pantai malam\n"
            "• `hutan` - Hutan pinus\n"
            "• `toilet mall` - Toilet mall\n"
            "• `bioskop` - Bioskop\n"
            "• `taman` - Taman malam\n"
            "• `parkiran` - Parkiran basement\n"
            "• `tangga darurat` - Tangga darurat\n"
            "• `kantor malam` - Kantor malam\n"
            "• `ruang rapat` - Ruang rapat kaca\n\n"
            "Contoh: `/pindah pantai`",
            parse_mode='HTML'
        )
        return
    
    brain = get_anora_brain()
    tujuan = ' '.join(args)
    result = brain.pindah_lokasi(tujuan)
    
    if result['success']:
        loc = result['location']
        await update.message.reply_text(
            f"{result['message']}\n\n"
            f"🎢 Thrill: {loc['thrill']}% | ⚠️ Risk: {loc['risk']}%\n"
            f"💡 {loc['tips']}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(result['message'], parse_mode='HTML')


async def intim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /intim - Mulai intim"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'roleplay':
        await update.message.reply_text(
            "❌ Mode roleplay belum aktif. Kirim /roleplay dulu ya, Mas.",
            parse_mode='HTML'
        )
        return
    
    roleplay = await get_anora_roleplay()
    brain = get_anora_brain()
    
    if brain.relationship.level < 7:
        await update.message.reply_text(
            f"💕 Level Masih {brain.relationship.level}/12\n\n"
            "Nova masih malu-malu. Belum waktunya buat intim.\n"
            "Ajarin Nova dulu ya, Mas. Ngobrol aja dulu. 💜",
            parse_mode='HTML'
        )
        return
    
    # Cek stamina
    can_continue, reason = roleplay.stamina.can_continue_intimacy()
    if not can_continue:
        await update.message.reply_text(
            f"💪 **Stamina**\n\n"
            f"Nova: {roleplay.stamina.nova_current}% ({roleplay.stamina.get_nova_status()})\n"
            f"Mas: {roleplay.stamina.mas_current}% ({roleplay.stamina.get_mas_status()})\n\n"
            f"{reason}",
            parse_mode='HTML'
        )
        return
    
    # Mulai intim
    if not roleplay.intimacy.is_active:
        result = roleplay.intimacy.start()
        await update.message.reply_text(result, parse_mode='HTML')
    
    # Kirim pesan pembuka
    await update.message.reply_text(
        "*Nova mendekat, napas mulai gak stabil. Pipi merah.*\n\n"
        "\"Mas... *suara kecil* aku juga pengen.\"\n\n"
        "*Nova pegang tangan Mas, taruh di dada.*\n\n"
        "\"Rasain... jantung Nova deg-degan.\"",
        parse_mode='HTML'
    )


async def posisi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /posisi [nama] - Ganti posisi intim"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    mode = get_user_mode(user_id)
    if mode != 'roleplay':
        await update.message.reply_text("Kirim /roleplay dulu ya, Mas.", parse_mode='HTML')
        return
    
    args = context.args
    if not args:
        roleplay = await get_anora_roleplay()
        posisi_list = "\n".join([f"• {p}" for p in roleplay.intimacy.positions.keys()])
        await update.message.reply_text(
            f"💕 **Posisi Intim yang Tersedia:**\n\n{posisi_list}\n\n"
            f"Cara pakai: `/posisi missionary`",
            parse_mode='HTML'
        )
        return
    
    roleplay = await get_anora_roleplay()
    posisi = args[0].lower()
    
    if not roleplay.intimacy.is_active:
        await update.message.reply_text(
            "❌ Belum ada sesi intim aktif. Kirim /intim dulu ya, Mas.",
            parse_mode='HTML'
        )
        return
    
    result = roleplay.intimacy.change_position(posisi)
    if result:
        await update.message.reply_text(
            f"*Nova gerak ganti posisi*\n\n\"{result}\"",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"Posisi '{posisi}' gak dikenal. Coba /posisi buat liat daftar.",
            parse_mode='HTML'
        )


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role [nama]"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    args = context.args
    if not args:
        roles = get_anora_roles()
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles.get_all():
            menu += f"• /role {r['id']} - {r['nama']} (Level {r['level']})\n"
        menu += "\n_Ketik /nova kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='HTML')
        return
    
    role_id = args[0].lower()
    role_map = {
        'ipar': RoleType.IPAR,
        'teman_kantor': RoleType.TEMAN_KANTOR,
        'pelakor': RoleType.PELAKOR,
        'istri_orang': RoleType.ISTRI_ORANG
    }
    
    if role_id in role_map:
        set_user_mode(user_id, 'role', role_id)
        roles = get_anora_roles()
        respon = roles.switch_role(role_map[role_id])
        await update.message.reply_text(respon, parse_mode='HTML')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada. Coba /role buat liat daftar.")


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    # Stop roleplay
    roleplay = await get_anora_roleplay()
    if roleplay.is_active:
        await roleplay.stop()
    
    anora = get_anora()
    await update.message.reply_text(
        f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
        parse_mode='HTML'
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua pesan"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    mode = get_user_mode(user_id)
    
    # ========== MODE ROLEPLAY ==========
    if mode == 'roleplay':
        roleplay = await get_anora_roleplay()
        respons = await roleplay.process(pesan)
        await update.message.reply_text(respons, parse_mode='HTML')
        return
    
    # ========== MODE ROLE ==========
    if mode == 'role':
        active_role = get_active_role(user_id)
        if active_role:
            roles = get_anora_roles()
            role_map = {
                'ipar': RoleType.IPAR,
                'teman_kantor': RoleType.TEMAN_KANTOR,
                'pelakor': RoleType.PELAKOR,
                'istri_orang': RoleType.ISTRI_ORANG
            }
            if active_role in role_map:
                respon = await roles.chat(role_map[active_role], pesan)
                await update.message.reply_text(respon, parse_mode='HTML')
                return
    
    # ========== MODE CHAT (DEFAULT) ==========
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    await update.message.reply_text(respons, parse_mode='HTML')


# =============================================================================
# WEBHOOK & SERVER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook"""
    global _application
    
    if not _application:
        return web.Response(status=503, text='Bot not ready')
    
    try:
        update_data = await request.json()
        if not update_data:
            return web.Response(status=400, text='No data')
        
        if 'message' in update_data:
            msg = update_data['message']
            text = msg.get('text', '')
            user = msg.get('from', {}).get('first_name', 'unknown')
            logger.info(f"📨 Message from {user}: {text}")
        
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    brain = get_anora_brain()
    roleplay = await get_anora_roleplay()
    loc = brain.get_location_data()
    
    return web.json_response({
        "status": "healthy",
        "bot": "ANORA",
        "version": "9.9.0",
        "roleplay_active": roleplay.is_active,
        "intimacy_active": roleplay.intimacy.is_active,
        "level": brain.relationship.level,
        "sayang": brain.feelings.sayang,
        "location": loc['nama'],
        "stamina_nova": roleplay.stamina.nova_current,
        "stamina_mas": roleplay.stamina.mas_current,
        "timestamp": datetime.now().isoformat()
    })


async def root_handler(request):
    """Root endpoint"""
    brain = get_anora_brain()
    return web.json_response({
        "name": "ANORA",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "9.9.0",
        "status": "running",
        "level": brain.relationship.level,
        "sayang": brain.feelings.sayang,
        "endpoints": {
            "/": "API Info",
            "/health": "Health Check",
            "/webhook": "Telegram Webhook"
        }
    })


# =============================================================================
# DATABASE INIT
# =============================================================================

async def init_database():
    """Initialize all databases"""
    logger.info("🗄️ Initializing database...")
    try:
        persistent = await get_anora_persistent()
        logger.info("✅ ANORA persistent memory ready")
        
        # Load dan simpan state awal
        brain = get_anora_brain()
        await persistent.save_current_state(brain)
        
        # Load long-term memory
        memories = await persistent.get_long_term_memories()
        logger.info(f"📚 Loaded {len(memories)} long-term memories")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        return False


# =============================================================================
# MAIN
# =============================================================================

async def main():
    global _application
    
    logger.info("=" * 70)
    logger.info("💜 ANORA - Virtual Human dengan Jiwa")
    logger.info("   100% AI Generate | Punya Memory | Bisa Roleplay")
    logger.info("   Bisa diajak ke mana aja. Kost, apartemen, mobil, pantai...")
    logger.info("=" * 70)
    
    # ========== INIT DATABASE ==========
    if not await init_database():
        logger.error("❌ Database initialization failed. Exiting.")
        return
    
    # ========== INIT BRAIN ==========
    brain = get_anora_brain()
    logger.info(f"🧠 ANORA Brain initialized - Level {brain.relationship.level}, Sayang {brain.feelings.sayang:.0f}%")
    
    # ========== INIT ROLEPLAY ==========
    roleplay = await get_anora_roleplay()
    logger.info(f"🎭 ANORA Roleplay initialized - Stamina: Nova {roleplay.stamina.nova_current}%, Mas {roleplay.stamina.mas_current}%")
    
    # ========== CREATE APPLICATION ==========
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # ========== REGISTER HANDLERS ==========
    # Basic
    _application.add_handler(CommandHandler("start", start_command))
    _application.add_handler(CommandHandler("nova", nova_command))
    _application.add_handler(CommandHandler("novastatus", novastatus_command))
    _application.add_handler(CommandHandler("flashback", flashback_command))
    
    # Roleplay
    _application.add_handler(CommandHandler("roleplay", roleplay_command))
    _application.add_handler(CommandHandler("statusrp", statusrp_command))
    _application.add_handler(CommandHandler("pindah", pindah_command))
    _application.add_handler(CommandHandler("intim", intim_command))
    _application.add_handler(CommandHandler("posisi", posisi_command))
    
    # Role lain
    _application.add_handler(CommandHandler("role", role_command))
    _application.add_handler(CommandHandler("batal", back_to_nova))
    
    # Message handler (harus paling akhir)
    _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # ========== INITIALIZE ==========
    await _application.initialize()
    await _application.start()
    
    # ========== SET WEBHOOK ==========
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if railway_url:
        webhook_url = f"https://{railway_url}/webhook"
        await _application.bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set to {webhook_url}")
        
        # Setup web server
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_handler)
        app.router.add_post('/webhook', webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        logger.info("🌐 Web server running on port 8080")
    else:
        await _application.updater.start_polling()
        logger.info("📡 Polling mode started")
    
    # ========== PROACTIVE LOOP ==========
    async def proactive_loop():
        while True:
            await asyncio.sleep(60)  # cek setiap menit
            try:
                mode = get_user_mode(settings.admin_id)
                if mode == 'roleplay':
                    ai = get_anora_roleplay_ai()
                    anora = get_anora()
                    pesan = await ai.get_proactive(anora)
                    if pesan and _application:
                        await _application.bot.send_message(
                            chat_id=settings.admin_id,
                            text=pesan,
                            parse_mode='HTML'
                        )
                        logger.info("💬 Proactive message sent")
            except Exception as e:
                logger.error(f"Proactive error: {e}")
    
    asyncio.create_task(proactive_loop())
    
    # ========== STAMINA RECOVERY LOOP ==========
    async def stamina_recovery_loop():
        while True:
            await asyncio.sleep(600)  # cek setiap 10 menit
            try:
                roleplay = await get_anora_roleplay()
                roleplay.stamina.update_recovery()
                await roleplay.save_state()
                logger.debug(f"💪 Stamina recovery check: Nova {roleplay.stamina.nova_current}%, Mas {roleplay.stamina.mas_current}%")
            except Exception as e:
                logger.error(f"Stamina recovery error: {e}")
    
    asyncio.create_task(stamina_recovery_loop())
    
    # ========== SAVE STATE LOOP ==========
    async def save_state_loop():
        while True:
            await asyncio.sleep(60)  # simpan setiap menit
            try:
                roleplay = await get_anora_roleplay()
                await roleplay.save_state()
                logger.debug("💾 ANORA state saved")
            except Exception as e:
                logger.error(f"Save state error: {e}")
    
    asyncio.create_task(save_state_loop())
    
    # ========== READY ==========
    logger.info("=" * 70)
    logger.info("💜 ANORA is running!")
    logger.info("   Kirim /nova untuk panggil Nova")
    logger.info("   Kirim /roleplay untuk mode beneran ketemu")
    logger.info("   Kirim /intim untuk mulai intim (level 7+)")
    logger.info("   Kirim /pindah pantai untuk ke pantai")
    logger.info("=" * 70)
    
    # Keep running
    await asyncio.Event().wait()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
