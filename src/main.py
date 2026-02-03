import sys
import os

# Добавляем папку src в путь импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from config import BOT_TOKEN
import database as db
from handlers import cmd_addmoney 
from handlers import (
    cmd_start,
    cmd_balance,
    cmd_stats,
    cmd_top,
    cmd_daily,
    handle_slots,
    handle_dice,
    handle_roulette,
    handle_bet,
    handle_dice_choice,
    handle_roulette_choice,
    handle_roulette_number
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Запуск бота"""
    print("🔧 Инициализация базы данных...")
    db.init_db()

    print("🤖 Запуск казино бота...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('balance', cmd_balance))
    application.add_handler(CommandHandler('stats', cmd_stats))
    application.add_handler(CommandHandler('top', cmd_top))
    application.add_handler(CommandHandler('daily', cmd_daily))
    application.add_handler(CommandHandler('addmoney', cmd_addmoney))

    # Кнопки главного меню
    application.add_handler(MessageHandler(filters.Regex("^🎰 Слоты$"), handle_slots))
    application.add_handler(MessageHandler(filters.Regex("^🎲 Кости$"), handle_dice))
    application.add_handler(MessageHandler(filters.Regex("^🎡 Рулетка$"), handle_roulette))
    application.add_handler(MessageHandler(filters.Regex("^💰 Баланс$"), cmd_balance))
    application.add_handler(MessageHandler(filters.Regex("^📊 Статистика$"), cmd_stats))
    application.add_handler(MessageHandler(filters.Regex("^🏆 Топ игроков$"), cmd_top))
    application.add_handler(MessageHandler(filters.Regex("^🎁 Ежедневный бонус$"), cmd_daily))

    # Inline кнопки (callback)
    application.add_handler(CallbackQueryHandler(handle_bet, pattern="^bet_"))
    application.add_handler(CallbackQueryHandler(handle_bet, pattern="^cancel$"))
    application.add_handler(CallbackQueryHandler(handle_dice_choice, pattern="^dice_"))
    application.add_handler(CallbackQueryHandler(handle_roulette_choice, pattern="^roul_"))

    # Ввод числа для рулетки
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_roulette_number))

    print("✅ Казино бот запущен!")
    print("💬 Напишите боту /start в Telegram")
    print("🛑 Для остановки нажмите Ctrl+C")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()