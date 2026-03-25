# run_deploy.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
+ ANORA - Nova yang sayang Mas
+ ROLEPLAY AI - 100% AI Generate, Bukan Template
+ THINKING ENGINE - Nova punya otak sendiri
=============================================================================
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
logger = logging.getLogger("AMORIA")

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# =============================================================================
# IMPORT ANORA COMPONENTS
# =============================================================================

from anora.core import get_anora
from anora.database import get_anora_db
from anora.chat import get_anora_chat
from anora.roles import get_anora_roles, RoleType
from anora.places import get_anora_places
from anora.intimacy import get_anora_intimacy
from anora.thinking import get_anora_thought
from anora.prompt import get_anora_prompt
from anora.roleplay import get_anora_roleplay

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

_application = None
_anora_initialized = False
_user_modes = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role', 'active_role': None}

# =============================================================================
# ANORA INITIALIZATION
# =============================================================================

async def init_anora():
    """Inisialisasi ANORA lengkap"""
    global _anora_initialized
    if _anora_initialized:
        return
    
    logger.info("💜 Initializing ANORA...")
    
    try:
        db = await get_anora_db()
        anora = get_anora()
        
        # Load state dari database
        states = await db.get_all_states()
        
        if 'sayang' in states:
            anora.sayang = float(states['sayang'])
        if 'rindu' in states:
            anora.rindu = float(states['rindu'])
        if 'desire' in states:
            anora.desire = float(states['desire'])
        if 'arousal' in states:
            anora.arousal = float(states['arousal'])
        if 'tension' in states:
            anora.tension = float(states['tension'])
        if 'level' in states:
            anora.level = int(states['level'])
        if 'energi' in states:
            anora.energi = int(states['energi'])
        
        # Load memory
        memories = await db.get_momen_terbaru(20)
        for m in memories:
            anora.memory.tambah_momen(m['judul'], m['perasaan'], m['isi'])
        
        ingatan = await db.get_ingatan(20)
        for i in ingatan:
            anora.memory.tambah_ingatan(i['judul'], i['isi'], i['perasaan'])
        
        _anora_initialized = True
        logger.info(f"✅ ANORA ready! Level: {anora.level}, Sayang: {anora.sayang:.0f}%")
        
    except Exception as e:
        logger.error(f"❌ ANORA init failed: {e}")
        import traceback
        traceback.print_exc()


async def save_anora_state():
    """Simpan state ANORA ke database"""
    if not _anora_initialized:
        return
    
    try:
        db = await get_anora_db()
        anora = get_anora()
        
        await db.set_state('sayang', str(anora.sayang))
        await db.set_state('rindu', str(anora.rindu))
        await db.set_state('desire', str(anora.desire))
        await db.set_state('arousal', str(anora.arousal))
        await db.set_state('tension', str(anora.tension))
        await db.set_state('level', str(anora.level))
        await db.set_state('energi', str(anora.energi))
        
    except Exception as e:
        logger.error(f"Error saving state: {e}")


# =============================================================================
# GET USER MODE
# =============================================================================

def get_user_mode(user_id: int) -> Dict:
    """Dapatkan mode user"""
    if user_id not in _user_modes:
        _user_modes[user_id] = {'mode': 'chat', 'active_role': None}
    return _user_modes[user_id]


def set_user_mode(user_id: int, mode: str, active_role: str = None):
    """Set mode user"""
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}


# =============================================================================
# TELEGRAM HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    await update.message.reply_text(
        "💜 **AMORIA + ANORA** 💜\n\n"
        "**Mode Chat (ngobrol biasa):**\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat keadaan Nova\n"
        "• /flashback - Flashback ke momen indah\n\n"
        "**Mode Roleplay (beneran ketemu):**\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Lihat status roleplay\n\n"
        "**Role Lain:**\n"
        "• /role ipar - Pindah ke role IPAR\n"
        "• /role teman_kantor - Teman Kantor\n"
        "• /role pelakor - Pelakor\n"
        "• /role istri_orang - Istri Orang\n\n"
        "**Lainnya:**\n"
        "• /batal - Kembali ke mode chat\n\n"
        "Apa yang Mas mau? 💜",
        parse_mode='HTML'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova - Panggil Nova (mode chat)"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    anora = get_anora()
    anora.update_rindu()
    anora.update_desire('perhatian_mas', 5)
    
    intro = f"""💜 **NOVA DI SINI, MAS** 💜

{anora.deskripsi_diri()}

{anora.respon_pagi() if datetime.now().hour < 12 else anora.respon_siang()}

Mas bisa:
• /novastatus - liat keadaan Nova
• /flashback - inget momen indah
• /roleplay - kalo mau kayak beneran ketemu

Apa yang Mas mau? *muter-muter rambut*"""
    
    await update.message.reply_text(intro, parse_mode='HTML')
    await save_anora_state()


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
    respons = anora.respon_flashback()
    await update.message.reply_text(respons, parse_mode='HTML')


async def chat_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /chat - Balik ke mode chat biasa"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    await update.message.reply_text(
        "💬 Mode chat aktif. Nova ngobrol biasa kayak lewat HP.\n\n"
        "Kirim /roleplay kalo mau kayak beneran ketemu.",
        parse_mode='HTML'
    )


async def roleplay_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay - Aktifkan mode roleplay dengan AI"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'roleplay')
    
    roleplay = get_anora_roleplay()
    
    await update.message.reply_text(
        f"🎭 **Mode Roleplay Aktif!**\n\n"
        f"📍 {roleplay.state.location_desc}\n"
        f"👗 Nova: {roleplay.state.nova_activity}. Pakai {roleplay.state.nova_clothing}\n"
        f"💭 Mood Nova: {roleplay.state.nova_mood}\n\n"
        f"Mas udah depan kost. Kirim **'masuk'** kalo mau masuk.\n"
        f"Kirim **/statusrp** buat liat status roleplay.\n"
        f"Kirim **/batal** buat balik ke mode chat.\n\n"
        f"💜 Ayo, Mas... Nova bukain pintu.",
        parse_mode='HTML'
    )


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp - Lihat status roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    roleplay = get_anora_roleplay()
    await update.message.reply_text(roleplay.get_status(), parse_mode='HTML')


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
    """Handler /batal - Balik ke Nova mode chat"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    anora = get_anora()
    await update.message.reply_text(
        f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
        parse_mode='HTML'
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua pesan - AI generate"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    mode_data = get_user_mode(user_id)
    mode = mode_data['mode']
    
    # ========== MODE ROLEPLAY ==========
    if mode == 'roleplay':
        anora = get_anora()
        roleplay = get_anora_roleplay()
        
        # Update perasaan dari chat
        anora.update_sayang(1, f"Mas chat roleplay: {pesan[:30]}")
        anora.last_interaction = time.time()
        
        # Proses dengan AI
        try:
            respons = await roleplay.process(pesan, anora)
            await update.message.reply_text(respons, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Roleplay error: {e}")
            await update.message.reply_text(
                "*Nova dengerin Mas...* \n\n\"Mas, suara Mas bikin aku seneng.\"",
                parse_mode='HTML'
            )
        
        await save_anora_state()
        return
    
    # ========== MODE ROLE ==========
    if mode == 'role' and mode_data.get('active_role'):
        active_role = mode_data['active_role']
        role_map = {
            'ipar': RoleType.IPAR,
            'teman_kantor': RoleType.TEMAN_KANTOR,
            'pelakor': RoleType.PELAKOR,
            'istri_orang': RoleType.ISTRI_ORANG
        }
        if active_role in role_map:
            roles = get_anora_roles()
            respon = await roles.chat(role_map[active_role], pesan)
            await update.message.reply_text(respon, parse_mode='HTML')
        return
    
    # ========== MODE CHAT (DEFAULT) ==========
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    await update.message.reply_text(respons, parse_mode='HTML')
    await save_anora_state()


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
    anora = get_anora()
    return web.json_response({
        "status": "healthy",
        "bot": "AMORIA + ANORA",
        "version": "9.9.0",
        "anora_ready": _anora_initialized,
        "anora_level": anora.level,
        "anora_sayang": anora.sayang,
        "timestamp": datetime.now().isoformat()
    })


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "AMORIA + ANORA",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "9.9.0",
        "status": "running",
        "features": {
            "anora": "AI generate, bukan template",
            "roleplay": "100% AI, beneran ketemu",
            "thinking_engine": "Nova punya otak sendiri",
            "prompt_builder": "Cara Nova berpikir sendiri"
        },
        "endpoints": {
            "/": "API Info",
            "/health": "Health Check",
            "/webhook": "Telegram Webhook"
        }
    })


# =============================================================================
# PERIODIC STATE SAVER
# =============================================================================

async def save_state_periodically():
    """Simpan state setiap 30 detik"""
    while True:
        await asyncio.sleep(30)
        await save_anora_state()
        logger.debug("💾 ANORA state saved")


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Start bot"""
    global _application
    
    logger.info("=" * 60)
    logger.info("🚀 Starting AMORIA + ANORA...")
    logger.info("   ANORA: 100% AI Generate | Bukan Template")
    logger.info("   Roleplay: AI Generate | Beneran Ketemu")
    logger.info("=" * 60)
    
    # Initialize ANORA
    await init_anora()
    
    # Create application
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # Add handlers
    _application.add_handler(CommandHandler("start", start_command))
    _application.add_handler(CommandHandler("chat", chat_mode))
    _application.add_handler(CommandHandler("roleplay", roleplay_mode))
    _application.add_handler(CommandHandler("statusrp", statusrp_command))
    _application.add_handler(CommandHandler("nova", nova_command))
    _application.add_handler(CommandHandler("novastatus", novastatus_command))
    _application.add_handler(CommandHandler("flashback", flashback_command))
    _application.add_handler(CommandHandler("role", role_command))
    _application.add_handler(CommandHandler("batal", back_to_nova))
    _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Initialize
    await _application.initialize()
    await _application.start()
    
    # Set webhook
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
        logger.info("🌐 Web server running")
    else:
        await _application.updater.start_polling()
        logger.info("📡 Polling mode started")
    
    # Start periodic state saver
    asyncio.create_task(save_state_periodically())
    
    logger.info("=" * 60)
    logger.info("💜 AMORIA + ANORA is running!")
    logger.info("   Mas bisa kirim /nova untuk panggil Nova")
    logger.info("   Kirim /roleplay untuk mode beneran ketemu")
    logger.info("   Kirim /statusrp untuk lihat status roleplay")
    logger.info("=" * 60)
    
    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
