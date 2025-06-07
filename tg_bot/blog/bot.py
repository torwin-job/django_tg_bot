from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import BadRequest
from .models import Post
import os
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
from django.db.models import Prefetch

# Загружаем переменные окружения из .env файла
load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = (
        "👋 Привет! Я бот для просмотра постов блога.\n\n"
        "Доступные команды:\n"
        "/posts - просмотр списка постов\n"
        "/post - создать новый пост\n"
        "/help - помощь"
    )
    await update.message.reply_text(welcome_text)

@sync_to_async
def get_all_posts():
    """Получение всех постов с предзагрузкой автора"""
    return list(Post.objects.select_related('author').all())

@sync_to_async
def get_post_by_id(post_id):
    """Получение поста по ID с предзагрузкой автора"""
    return Post.objects.select_related('author').get(id=post_id)

async def send_posts_list(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False):
    """Отправка списка постов"""
    posts = await get_all_posts()
    if not posts:
        if is_callback:
            await update.callback_query.message.reply_text("😔 Пока нет доступных постов.")
        else:
            await update.message.reply_text("😔 Пока нет доступных постов.")
        return

    # Создаем inline клавиатуру с постами
    keyboard = []
    for post in posts:
        keyboard.append([
            InlineKeyboardButton(
                f"📌 {post.title}",
                callback_data=f"post_{post.id}"
            )
        ])
    
    # Добавляем кнопку "Обновить список"
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
        if "Message is not modified" in str(e):
            # Игнорируем ошибку, если сообщение не изменилось
            pass
        else:
            # Пробрасываем другие ошибки
            raise

async def posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /posts"""
    await send_posts_list(update, context, is_callback=False)

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /post"""
    await update.message.reply_text(
        "📝 Создание нового поста\n\n"
        "Отправьте сообщение в формате:\n"
        "Заголовок\n"
        "---\n"
        "Содержание поста"
    )
    # Устанавливаем состояние ожидания ввода поста
    context.user_data['waiting_for_post'] = True

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "refresh_posts" or query.data == "back_to_list":
        await send_posts_list(update, context, is_callback=True)
        return
    
    post_id = int(query.data.split('_')[1])
    post = await get_post_by_id(post_id)
    
    # Создаем inline клавиатуру для поста
    keyboard = [
        [
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_list")
        ]
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
        if "Message is not modified" in str(e):
            # Игнорируем ошибку, если сообщение не изменилось
            pass
        else:
            # Пробрасываем другие ошибки
            raise

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/posts - просмотр списка постов\n"
        "/post - создать новый пост\n"
        "/help - показать это сообщение\n\n"
        "Для создания поста используйте команду /post и следуйте инструкциям."
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    if context.user_data.get('waiting_for_post'):
        text = update.message.text
        if '---' in text:
            title, content = text.split('---', 1)
            title = title.strip()
            content = content.strip()
            
            # TODO: Добавить создание поста через API
            await update.message.reply_text(
                f"✅ Пост создан!\n\n"
                f"Заголовок: {title}\n"
                f"Содержание: {content[:100]}..."
            )
            context.user_data['waiting_for_post'] = False
        else:
            await update.message.reply_text(
                "❌ Неверный формат. Используйте разделитель '---' между заголовком и содержанием."
            )
    else:
        await update.message.reply_text(
            "❓ Используйте /help для просмотра доступных команд."
        )

def run_bot():
    """Запуск бота"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
    
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("posts", posts))
    application.add_handler(CommandHandler("post", post))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик callback-запросов
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES) 