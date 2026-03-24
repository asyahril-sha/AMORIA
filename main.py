# main.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Main Entry Point with Enhanced Error Logging for Railway
=============================================================================
"""

import os
import sys
import asyncio
import signal
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional

from aiohttp import web
from telegram import Update
from telegram.ext import Application
from telegram.request import HTTPXRequest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import error logger first
from utils.error_logger import (
    get_error_logger, 
    log_error, 
    log_info, 
    log_warning, 
    log_debug,
    print_startup_banner,
    handle_errors
)

# Initialize error logger
error_logger = get_error_logger()
print_startup_banner()

# Import other modules with error handling
try:
    from config import settings
    from utils.logger import setup_logging
    from bot.application import create_application
    from bot.webhook import setup_webhook_sync, setup_polling, check_webhook_status
    from database.migrate import run_migrations
    
    log_info("✅ All modules imported successfully")
    
except Exception as e:
    error_logger.log_error(e, {'stage': 'import_modules'}, severity="CRITICAL")
    sys.exit(1)

logger = setup_logging("AMORIA")


class AmoriaBot:
    """
    Main bot class untuk AMORIA 9.9
    Virtual Human dengan Jiwa
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.application: Optional[Application] = None
        self.is_ready = False
        self._shutdown_flag = False
        self.db_initialized = False
        
        log_info("=" * 70)
        log_info("💜 AMORIA - Virtual Human dengan Jiwa 9.9")
        log_info("   100% AI Generate | Multi-Identity | Soul Bounded")
        log_info("=" * 70)
    
    async def init_database(self) -> bool:
        """Initialize database with all tables"""
        log_info("🗄️ Initializing database...")
        
        try:
            # Run migrations
            success = await run_migrations()
            
            if success:
                self.db_initialized = True
                log_info("✅ Database initialized with state persistence")
            else:
                log_warning("⚠️ Database initialization incomplete")
            
            return success
            
        except Exception as e:
            error_logger.log_error(e, {'stage': 'database_init'}, severity="CRITICAL")
            return False
    
    async def init_application(self) -> Application:
        """Create and initialize bot application"""
        log_info("🔧 Creating bot application...")
        
        try:
            self.application = create_application()
            await self.application.initialize()
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            log_info("✅ Bot application created")
            return self.application
            
        except Exception as e:
            error_logger.log_error(e, {'stage': 'application_init'}, severity="CRITICAL")
            raise
    
    @handle_errors(severity="ERROR")
    async def error_handler(self, update: Update, context) -> None:
        """Global error handler with logging to Railway"""
        error = context.error
        
        # Log error ke Railway
        error_details = error_logger.log_error(
            error,
            {
                'update_id': update.update_id if update else None,
                'user_id': update.effective_user.id if update and update.effective_user else None,
                'chat_id': update.effective_chat.id if update and update.effective_chat else None,
                'message_text': update.message.text[:200] if update and update.message and update.message.text else None,
                'callback_data': update.callback_query.data[:200] if update and update.callback_query and update.callback_query.data else None
            },
            severity="ERROR"
        )
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ **Terjadi error internal**\n\n"
                    "Maaf, terjadi kesalahan. Error sudah dicatat di log.\n\n"
                    "Silakan coba lagi nanti, Mas.\n\n"
                    f"_Error ID: {error_details['error_id']}_",
                    parse_mode='HTML'
                )
        except Exception as e:
            error_logger.log_error(e, {'stage': 'send_error_message'})
    
    async def setup_webhook(self) -> bool:
        """Setup webhook untuk Telegram"""
        try:
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            
            if not railway_url and not settings.webhook.url:
                log_warning("⚠️ No webhook URL configured, using polling mode")
                return await setup_polling(self.application)
            
            webhook_url = f"https://{railway_url}{settings.webhook.path}" if railway_url else settings.webhook.url
            
            log_info(f"🔗 Setting webhook to: {webhook_url}")
            
            # Delete old webhook
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            log_info("✅ Old webhook deleted")
            
            # Set new webhook
            await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True,
                max_connections=40,
                timeout=30
            )
            
            # Verify
            info = await self.application.bot.get_webhook_info()
            if info.url == webhook_url:
                log_info(f"✅ Webhook verified: {info.url}")
                log_info(f"   Pending updates: {info.pending_update_count}")
                return True
            else:
                log_error(f"❌ Webhook verification failed: {info.url}")
                return False
                
        except Exception as e:
            error_logger.log_error(e, {'stage': 'webhook_setup'}, severity="ERROR")
            return False
    
    async def webhook_handler(self, request) -> web.Response:
        """AIOHTTP webhook handler with error logging"""
        if not self.application:
            return web.Response(status=503, text='Bot not ready')
        
        try:
            update_data = await request.json()
            if not update_data:
                return web.Response(status=400, text='No data')
            
            update = Update.de_json(update_data, self.application.bot)
            asyncio.create_task(self.application.process_update(update))
            
            log_debug(f"✅ Processed update: {update.update_id}")
            return web.Response(text='OK')
            
        except Exception as e:
            error_logger.log_error(e, {'stage': 'webhook_handler'})
            return web.Response(status=500, text=str(e))
    
    async def health_handler(self, request) -> web.Response:
        """Health check endpoint with status detail"""
        from database.repository import Repository
        
        db_status = "unknown"
        db_stats = {}
        
        try:
            repo = Repository()
            stats = await repo.get_stats()
            db_status = "ok"
            db_stats = {
                "total_sessions": stats.get('registrations_count', 0),
                "active_sessions": stats.get('active_registrations', 0),
                "db_size_mb": stats.get('db_size_mb', 0)
            }
        except Exception as e:
            db_status = f"error: {str(e)[:50]}"
            error_logger.log_error(e, {'stage': 'health_check_db'})
        
        # Get error stats
        error_stats = error_logger.get_stats()
        
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "AMORIA",
            "version": "9.9.0",
            "bot_ready": self.application is not None,
            "database": {
                "status": db_status,
                **db_stats
            },
            "errors": {
                "total_errors": error_stats['total_errors'],
                "railway_mode": error_stats['railway_mode']
            },
            "features": {
                "multi_identity": True,
                "emotional_flow": True,
                "spatial_awareness": True,
                "soul_bounded": True,
                "aftercare_system": True,
                "100_percent_ai_generate": True
            },
            "uptime": str(datetime.now() - self.start_time)
        })
    
    async def root_handler(self, request) -> web.Response:
        """Root endpoint - API info"""
        error_stats = error_logger.get_stats()
        
        return web.json_response({
            "name": "AMORIA",
            "description": "Virtual Human dengan Jiwa",
            "version": "9.9.0",
            "status": "running",
            "admin_id": str(settings.admin_id),
            "errors_today": error_stats['total_errors'],
            "uptime": str(datetime.now() - self.start_time)
        })
    
    async def start(self):
        """Start bot and aiohttp server with enhanced logging"""
        try:
            self.print_banner()
            
            log_info("=" * 70)
            log_info("📡 STAGE 1/5: Initializing database...")
            log_info("=" * 70)
            
            if not await self.init_database():
                log_warning("⚠️ Database initialization incomplete, but continuing...")
            
            log_info("=" * 70)
            log_info("📡 STAGE 2/5: Creating application...")
            log_info("=" * 70)
            
            await self.init_application()
            
            log_info("=" * 70)
            log_info("📡 STAGE 3/5: Setting up webhook/polling...")
            log_info("=" * 70)
            
            webhook_success = await self.setup_webhook()
            
            if webhook_success:
                log_info("✅ Webhook mode activated!")
            else:
                log_info("📡 Using polling mode...")
                await setup_polling(self.application)
            
            log_info("=" * 70)
            log_info("📡 STAGE 4/5: Starting aiohttp server...")
            log_info("=" * 70)
            
            port = int(os.getenv('PORT', 8080))
            
            app = web.Application()
            app.router.add_post(settings.webhook.path, self.webhook_handler)
            app.router.add_get('/health', self.health_handler)
            app.router.add_get('/', self.root_handler)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            log_info(f"✅ AIOHTTP server running on port {port}")
            log_info(f"   • Healthcheck: /health")
            log_info(f"   • API Info: /")
            log_info(f"   • Webhook: {settings.webhook.path}")
            
            log_info("=" * 70)
            log_info("📡 STAGE 5/5: Bot is ready!")
            log_info("=" * 70)
            log_info("💜 AMORIA 9.9 is running on Railway!")
            log_info("   Press Ctrl+C to stop.")
            log_info("=" * 70)
            
            self.is_ready = True
            
            # Keep running
            while not self._shutdown_flag:
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            log_info("👋 Bot stopped by user")
        except Exception as e:
            error_logger.log_error(e, {'stage': 'bot_start'}, severity="CRITICAL")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown with logging"""
        log_info("🛑 Shutting down AMORIA...")
        self._shutdown_flag = True
        
        # Close database connection
        try:
            from database.connection import close_db
            await close_db()
            log_info("✅ Database connection closed")
        except Exception as e:
            error_logger.log_error(e, {'stage': 'shutdown_db'})
        
        # Stop application
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                log_info("✅ Application stopped")
            except Exception as e:
                error_logger.log_error(e, {'stage': 'shutdown_app'})
        
        # Print final error stats
        error_stats = error_logger.get_stats()
        log_info(f"📊 Final error stats: {error_stats['total_errors']} total errors")
        log_info("👋 Goodbye from AMORIA!")
    
    def print_banner(self):
        """Print startup banner untuk Railway log"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    █████╗ ███╗   ███╗ ██████╗ ██████╗ ██╗ █████╗                ║
║   ██╔══██╗████╗ ████║██╔═══██╗██╔══██╗██║██╔══██╗               ║
║   ███████║██╔████╔██║██║   ██║██████╔╝██║███████║               ║
║   ██╔══██║██║╚██╔╝██║██║   ██║██╔══██╗██║██╔══██║               ║
║   ██║  ██║██║ ╚═╝ ██║╚██████╔╝██║  ██║██║██║  ██║               ║
║   ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝               ║
║                                                                  ║
║                   Virtual Human dengan Jiwa                      ║
║                             9.9                                  ║
║                                                                  ║
║   • 9 Karakter dengan Kepribadian Unik                          ║
║   • 100% AI Generate - Setiap Respons Unik                      ║
║   • Multi-Identity System                                       ║
║   • Emotional Flow (Arousal 0-100)                              ║
║   • Soul Bounded (Level 11 - 30-50 Chat Intim)                  ║
║   • Aftercare dengan Mood Dinamis                               ║
║   • Clothing Hierarchy & History                                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        logger.info(banner)
        
        log_info("=" * 70)
        log_info("📊 CONFIGURATION:")
        log_info(f"   • Database: {settings.database.type} @ {settings.database.path}")
        log_info(f"   • AI Model: {settings.ai.model} | Temperature: {settings.ai.temperature}")
        log_info(f"   • Admin ID: {settings.admin_id}")
        log_info(f"   • Working Memory: {settings.memory.working_memory_size} chat")
        log_info(f"   • Level 10 Target: {settings.level.level_10_target} chat")
        log_info(f"   • Soul Bounded: {settings.level.level_11_min}-{settings.level.level_11_max} chat")
        log_info(f"   • Aftercare: {settings.level.level_12_min}-{settings.level.level_12_max} chat")
        log_info(f"   • Railway Mode: {os.getenv('RAILWAY_ENVIRONMENT', 'Not detected')}")
        log_info("=" * 70)


def signal_handler():
    """Handle shutdown signals with logging"""
    log_info("Received shutdown signal, shutting down...")


async def main():
    """Main entry point with error handling"""
    bot = AmoriaBot()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await bot.start()
    except asyncio.CancelledError:
        log_info("👋 Bot stopped by user")
    except Exception as e:
        error_logger.log_error(e, {'stage': 'main'}, severity="CRITICAL")
        raise
    finally:
        log_info("👋 Goodbye from AMORIA!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("Bot stopped by keyboard interrupt")
    except Exception as e:
        error_logger.log_error(e, {'stage': 'main_entry'}, severity="CRITICAL")
        sys.exit(1)
