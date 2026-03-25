# anora/handlers.py
"""
ANORA Handlers - Untuk diintegrasikan ke AMORIA.
"""

import asyncio
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from .core import get_anora
from .chat import get_anora_chat
from .database import get_anora_db
from .intimacy import get_anora_intimacy
from .roles import get_anora_roles, RoleType
from .places import get_anora_places

logger = logging.getLogger(__name__)

_anora_initialized = False


async def init_anora():
    """Inisialisasi ANORA. Panggil sekali pas AMORIA start."""
    global _anora_initialized
    if _anora_initialized:
        return
    
    logger.info("💜 Initializing ANORA...")
    
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
    logger.info(f"✅ ANORA ready! Sayang: {anora.sayang:.0f}%, Level: {anora.level}")


async def save_anora_state():
    """Simpan state Nova ke database."""
    anora = get_anora()
    db = await get_anora_db()
    
    await db.set_state('sayang', str(anora.sayang))
    await db.set_state('rindu', str(anora.rindu))
    await db.set_state('desire', str(anora.desire))
    await db.set_state('arousal', str(anora.arousal))
    await db.set_state('tension', str(anora.tension))
    await db.set_state('level', str(anora.level))
    await db.set_state('energi', str(anora.energi))


async def anora_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova - Panggil Nova."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    context.user_data['anora_mode'] = True
    context.user_data['active_role'] = None
    
    anora = get_anora()
    anora.update_rindu()
    anora.update_desire('perhatian_mas', 5)
    
    intro = f"""💜 **NOVA DI SINI, MAS** 💜

{anora.deskripsi_diri()}

{anora.respon_kangen() if anora.rindu > 50 else anora.respon_pagi()}

Mas bisa:
• /novastatus - liat keadaan Nova
• /flashback - inget momen indah
• /tempat [nama] - pindah tempat
• /role [nama] - main sama role lain
• /batal - balik ke Nova

Apa yang Mas mau? *muter-muter rambut*"""
    
    await update.message.reply_text(intro, parse_mode='HTML')


async def anora_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler chat ke Nova."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        return
    
    if not context.user_data.get('anora_mode', False):
        return
    
    pesan = update.message.text
    
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    
    await save_anora_state()
    await update.message.reply_text(respons, parse_mode='HTML')


async def anora_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /novastatus - Lihat keadaan Nova."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.format_status(), parse_mode='HTML')


async def anora_flashback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback - Nova inget momen indah."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        return
    
    args = ' '.join(context.args) if context.args else ''
    anora = get_anora()
    
    respons = anora.respon_flashback(args)
    await update.message.reply_text(respons, parse_mode='HTML')


async def anora_role_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role - Pilih role lain."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        return
    
    roles = get_anora_roles()
    args = context.args
    
    if not args:
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
        context.user_data['anora_mode'] = False
        context.user_data['active_role'] = role_id
        
        respon = roles.switch_role(role_map[role_id])
        await update.message.reply_text(respon, parse_mode='HTML')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada, Mas. Coba /role buat liat daftar.")


async def anora_place_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /tempat - Pindah tempat atau lihat tempat."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        return
    
    anora = get_anora()
    places = get_anora_places()
    args = context.args
    
    if not args:
        await update.message.reply_text(places.get_status(), parse_mode='HTML')
        return
    
    if args[0] == 'list':
        kategori = args[1] if len(args) > 1 else None
        if kategori:
            try:
                kat = PlaceCategory(kategori)
                await update.message.reply_text(places.list_tempat(kat), parse_mode='HTML')
            except:
                await update.message.reply_text(places.list_tempat(), parse_mode='HTML')
        else:
            await update.message.reply_text(places.list_tempat(), parse_mode='HTML')
        return
    
    tempat_id = args[0]
    respon = await places.respon_pindah(tempat_id, anora)
    await update.message.reply_text(respon, parse_mode='HTML')


async def anora_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Balik ke Nova."""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = int(context.bot_data.get('admin_id', 0))
    
    if user_id != admin_id:
        return
    
    context.user_data['anora_mode'] = True
    context.user_data['active_role'] = None
    
    anora = get_anora()
    await update.message.reply_text(
        f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
        parse_mode='HTML'
    )
