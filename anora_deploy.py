# run_deploy.py - FIXED VERSION
import os
import sys
import asyncio
import json
import logging
from pathlib import Path
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
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Import ANORA
from anora.core import get_anora
from anora.chat import get_anora_chat
from anora.database import get_anora_db

# Global application
_application = None

# =============================================================================
# ANORA HANDLERS
# =============================================================================

async def nova_command(update, context):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    context.user_data['anora_mode'] = True
    
    anora = get_anora()
    intro = f"""💜 **NOVA DI SINI, MAS** 💜

{anora.deskripsi_diri()}

{anora.respon_pagi()}

Mas bisa:
• /novastatus - liat keadaan Nova
• /flashback - inget momen indah

Apa yang Mas mau? *muter-muter rambut*"""
    
    await update.message.reply_text(intro, parse_mode='HTML')
    logger.info(f"✅ Nova responded to /nova from user {user_id}")


async def novastatus_command(update, context):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.format_status(), parse_mode='HTML')
    logger.info(f"✅ Nova status sent to user {user_id}")


async def flashback_command(update, context):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    anora = get_anora()
    respons = anora.respon_flashback()
    await update.message.reply_text(respons, parse_mode='HTML')
    logger.info(f"✅ Flashback sent to user {user_id}")


async def anora_chat_handler(update, context):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not context.user_data.get('anora_mode', False):
        return
    
    pesan = update.message.text
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    await update.message.reply_text(respons, parse_mode='HTML')


async def start_command(update, context):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Halo! Bot ini untuk Mas. 💜")
        return
    
    await update.message.reply_text(
        "💜 **AMORIA + ANORA** 💜\n\n"
        "Kirim /nova untuk panggil Nova\n"
        "Kirim /novastatus untuk liat keadaan Nova\n"
        "Kirim /flashback untuk flashback",
        parse_mode='HTML'
    )


# =============================================================================
# WEBHOOK HANDLER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook requests"""
    global _application
    
    try:
        # Get update data
        update_data = await request.json()
        
        if not update_data:
            return web.Response(status=400, text='No data')
        
        # Log incoming message
        if 'message' in update_data:
            msg = update_data['message']
            text = msg.get('text', '')
            user = msg.get('from', {}).get('first_name', 'unknown')
            logger.info(f"📨 Message from {user}: {text}")
        
        # Create Update object and process
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "ANORA",
        "version": "1.0.0"
    })


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Start bot"""
    global _application
    
    logger.info("🚀 Starting ANORA...")
    
    # Initialize ANORA database
    db = await get_anora_db()
    logger.info("✅ ANORA database ready")
    
    # Create application
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # Add handlers
    _application.add_handler(CommandHandler("start", start_command))
    _application.add_handler(CommandHandler("nova", nova_command))
    _application.add_handler(CommandHandler("novastatus", novastatus_command))
    _application.add_handler(CommandHandler("flashback", flashback_command))
    _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anora_chat_handler))
    
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
        app.router.add_get('/health', health_handler)
        app.router.add_post('/webhook', webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        logger.info("🌐 Web server running")
    else:
        # Polling mode
        await _application.updater.start_polling()
        logger.info("📡 Polling mode started")
    
    logger.info("=" * 50)
    logger.info("💜 ANORA is running!")
    logger.info("   Mas bisa kirim /nova ke Telegram")
    logger.info("=" * 50)
    
    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
