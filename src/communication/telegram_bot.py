from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

logger=logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, command_dispatcher):
        self.token=token
        self.dispatcher=command_dispatcher
        self.app=None
        self.user_sessions={}
    
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("cancel", self.cmd_cancel))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id=update.effective_user.id
        self.user_sessions[user_id]={'state': 'awaiting_address'}
        await update.message.reply_text(
            "🤖 Доставочный робот готов!\n\n"
            "Отправьте адрес доставки текстом или геолокацией."
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        status=await self.dispatcher.get_status()
        battery=status.get('battery', 'N/A')
        position=status.get('position', 'N/A')
        rover_status=status.get('status', 'unknown')
        target=status.get('target', 'нет')
        
        await update.message.reply_text(
            f"📊 Статус робота:\n"
            f"🔋 Заряд: {battery}%\n"
            f"📍 Позиция: {position}\n"
            f"🚀 Статус: {rover_status}\n"
            f"🎯 Цель: {target}"
        )
    
    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result=await self.dispatcher.cancel_mission()
        await update.message.reply_text(result)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id=update.effective_user.id
        address=update.message.text
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("Используйте /start для начала работы")
            return
        
        await update.message.reply_text(f"🔍 Строю маршрут до: {address}")
        
        try:
            result=await self.dispatcher.handle_new_order(address)
            await update.message.reply_text(f"✅ {result}")
        except Exception as e:
            logger.error(f"Error handling address: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        location=update.message.location
        lat=location.latitude
        lon=location.longitude
        
        await update.message.reply_text(f"🔍 Строю маршрут до координат: {lat}, {lon}")
        
        try:
            result=await self.dispatcher.handle_new_order_coordinates(lat, lon)
            await update.message.reply_text(f"✅ {result}")
        except Exception as e:
            logger.error(f"Error handling location: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    def start_polling(self):
        self.app=Application.builder().token(self.token).build()
        self._setup_handlers()
        logger.info("Bot started polling")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_webhook(self, webhook_url: str, port: int=8443):
        self.app=Application.builder().token(self.token).build()
        self._setup_handlers()
        logger.info(f"Bot started webhook on {webhook_url}")
        await self.app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="telegram_webhook",
            webhook_url=f"{webhook_url}/telegram_webhook"
        )