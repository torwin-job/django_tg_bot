from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import BadRequest
import os
from dotenv import load_dotenv
from .services import get_all_posts, get_post_by_id

# Загружаем переменные окружения из .env файла
load_dotenv()

class TelegramBot:
    """Основной класс бота"""
    
    def __init__(self):
        """Инициализация бота"""
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Настройка обработчиков команд"""
        # Регистрируем обработчики команд
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(CommandHandler("posts", self._handle_posts))
        self.application.add_handler(CommandHandler("help", self._handle_help))
        
        # Регистрируем обработчик callback-запросов
        self.application.add_handler(CallbackQueryHandler(self._handle_callback))

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = (
            "👋 Привет! Я бот для просмотра постов блога.\n\n"
            "Доступные команды:\n"
            "/posts - просмотр списка постов\n"
            "/help - помощь"
        )
        await update.message.reply_text(welcome_text)

    async def _handle_posts(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False):
        """Обработчик команды /posts"""
        posts = await get_all_posts()
        if not posts:
            message = "😔 Пока нет доступных постов."
            if is_callback:
                await update.callback_query.message.reply_text(message)
            else:
                await update.message.reply_text(message)
            return

        keyboard = []
        for post in posts:
            keyboard.append([
                InlineKeyboardButton(
                    f"📌 {post.title}",
                    callback_data=f"post_{post.id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(
                "🔄 Обновить список",
                callback_data="refresh_posts"
            )
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        message_text = "📚 Выберите пост для просмотра:"
        
        try:
            if is_callback:
                await update.callback_query.message.edit_text(
                    text=message_text,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    text=message_text,
                    reply_markup=reply_markup
                )
        except BadRequest as e:
            if "Message is not modified" not in str(e):
                raise

    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📚 <b>Доступные команды:</b>\n\n"
            "/posts - просмотр списка постов\n"
            "/help - показать это сообщение"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_posts" or query.data == "back_to_list":
            await self._handle_posts(update, context, is_callback=True)
            return
        
        if query.data.startswith("post_"):
            post_id = int(query.data.split('_')[1])
            post = await get_post_by_id(post_id)
            
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_list")]
            ]
            
            message = (
                f"📝 <b>{post.title}</b>\n\n"
                f"{post.content}\n\n"
                f"👤 Автор: {post.author.username}\n"
                f"📅 Создан: {post.created_at.strftime('%d.%m.%Y %H:%M')}"
            )
            
            try:
                await query.edit_message_text(
                    text=message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
            except BadRequest as e:
                if "Message is not modified" not in str(e):
                    raise

    def run(self):
        """Запуск бота"""
        print("🤖 Бот запущен...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def run_bot():
    """Функция для запуска бота"""
    bot = TelegramBot()
    bot.run() 