from telegram import Update
from telegram.ext import ContextTypes
import database as db
import games
from keyboards import (
    get_main_menu,
    get_bet_keyboard,
    get_dice_choice_keyboard,
    get_roulette_keyboard
)
from config import DAILY_BONUS

# ==================== КОМАНДЫ ====================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    db.register_user(user.id, user.username or user.first_name)

    await update.message.reply_text(
        f"🎰 Добро пожаловать в Казино, {user.first_name}!\n\n"
        f"💰 Ваш стартовый баланс: {db.get_balance(user.id)} монет\n\n"
        f"Выберите игру:",
        reply_markup=get_main_menu()
    )

async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать баланс"""
    user_id = update.effective_user.id
    balance, games_played, wins, losses = db.get_user_stats(user_id)

    win_rate = (wins / games_played * 100) if games_played > 0 else 0

    await update.message.reply_text(
        f"💰 *Ваш баланс*\n\n"
        f"💵 Монеты: {balance}\n"
        f"🎮 Игр сыграно: {games_played}\n"
        f"✅ Побед: {wins}\n"
        f"❌ Поражений: {losses}\n"
        f"📊 Процент побед: {win_rate:.1f}%",
        parse_mode="Markdown"
    )

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика"""
    await cmd_balance(update, context)

async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Топ игроков"""
    top_players = db.get_top_players(10)

    if not top_players:
        await update.message.reply_text("🏆 Топ игроков пока пуст!")
        return

    text = "🏆 *Топ 10 игроков:*\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for idx, (username, balance, total_games, wins) in enumerate(top_players, 1):
        medal = medals[idx - 1] if idx <= 3 else f"{idx}."
        text += f"{medal} {username} - {balance} 💰 (игр: {total_games})\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ежедневный бонус"""
    user_id = update.effective_user.id
    success, time_left = db.claim_daily_bonus(user_id)

    if success:
        await update.message.reply_text(
            f"🎁 Вы получили ежедневный бонус!\n"
            f"💰 +{DAILY_BONUS} монет\n\n"
            f"Возвращайтесь завтра за новым бонусом!"
        )
    else:
        await update.message.reply_text(
            f"⏰ Вы уже получали бонус сегодня!\n"
            f"Следующий бонус через: {time_left}"
        )

# ==================== ЗАПУСК ИГР ====================

async def handle_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск слотов"""
    context.user_data['game'] = 'slots'
    await update.message.reply_text(
        "🎰 *Слоты*\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard(),
        parse_mode="Markdown"
    )

async def handle_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск костей"""
    context.user_data['game'] = 'dice'
    await update.message.reply_text(
        "🎲 *Кости*\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard(),
        parse_mode="Markdown"
    )

async def handle_roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск рулетки"""
    context.user_data['game'] = 'roulette'
    await update.message.reply_text(
        "🎡 *Рулетка*\n\n"
        "Выберите ставку:",
        reply_markup=get_bet_keyboard(),
        parse_mode="Markdown"
    )

# ==================== ОБРАБОТКА СТАВОК ====================

async def handle_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора ставки"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text(
            "❌ Отменено.\n\nВыберите игру:",
            reply_markup=None
        )
        return

    # Получаем ставку из callback_data
    bet = int(query.data.split('_')[1])
    user_id = update.effective_user.id
    balance = db.get_balance(user_id)

    # Проверяем баланс
    if balance < bet:
        await query.edit_message_text(
            f"❌ Недостаточно средств!\n"
            f"Ваш баланс: {balance} 💰\n\n"
            f"Выберите меньшую ставку:",
            reply_markup=get_bet_keyboard()
        )
        return

    context.user_data['bet'] = bet
    game = context.user_data.get('game')

    if game == 'slots':
        await play_slots_game(query, context, user_id, bet)
    elif game == 'dice':
        await query.edit_message_text(
            f"🎲 Ставка: {bet} 💰\n\n"
            f"Выберите:",
            reply_markup=get_dice_choice_keyboard()
        )
    elif game == 'roulette':
        await query.edit_message_text(
            f"🎡 Ставка: {bet} 💰\n\n"
            f"Выберите тип ставки:",
            reply_markup=get_roulette_keyboard()
        )

# ==================== ИГРЫ ====================

async def play_slots_game(query, context, user_id, bet):
    """Играть в слоты"""
    db.update_balance(user_id, -bet)

    result, win, desc = games.play_slots(bet)

    if win > 0:
        db.update_balance(user_id, win)

    db.add_game_result(user_id, 'slots', bet, win, result)

    new_balance = db.get_balance(user_id)
    profit = win - bet

    await query.edit_message_text(
        f"{desc}\n\n"
        f"💰 Баланс: {new_balance} ({profit:+d})\n\n"
        f"Играть ещё?",
        reply_markup=get_bet_keyboard()
    )

async def handle_dice_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора в костях"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Отменено.")
        return

    choice = query.data.split('_')[1]  # high или low
    bet = context.user_data.get('bet')
    user_id = update.effective_user.id

    db.update_balance(user_id, -bet)

    dice_num, win, desc = games.play_dice(bet, choice)

    if win > 0:
        db.update_balance(user_id, win)

    db.add_game_result(user_id, 'dice', bet, win, str(dice_num))

    new_balance = db.get_balance(user_id)
    profit = win - bet

    await query.edit_message_text(
        f"{desc}\n\n"
        f"💰 Баланс: {new_balance} ({profit:+d})"
    )

async def handle_roulette_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора в рулетке"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Отменено.")
        return

    if query.data == "roul_number":
        await query.edit_message_text("🎯 Введите число от 0 до 36:")
        context.user_data['waiting_number'] = True
        return

    choice = query.data.split('_')[1]  # red, black, even, odd
    bet = context.user_data.get('bet')
    user_id = update.effective_user.id

    db.update_balance(user_id, -bet)

    number, color, win, desc = games.play_roulette(bet, choice)

    if win > 0:
        db.update_balance(user_id, win)

    db.add_game_result(user_id, 'roulette', bet, win, f"{number} ({color})")

    new_balance = db.get_balance(user_id)
    profit = win - bet

    await query.edit_message_text(
        f"{desc}\n\n"
        f"💰 Баланс: {new_balance} ({profit:+d})"
    )

async def handle_roulette_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода числа для рулетки"""
    if not context.user_data.get('waiting_number'):
        return

    try:
        number = int(update.message.text)
        if number < 0 or number > 36:
            await update.message.reply_text("⚠️ Введите число от 0 до 36")
            return
    except ValueError:
        await update.message.reply_text("⚠️ Введите корректное число")
        return

    context.user_data['waiting_number'] = False
    bet = context.user_data.get('bet')
    user_id = update.effective_user.id

    db.update_balance(user_id, -bet)

    result_num, color, win, desc = games.play_roulette(bet, number)

    if win > 0:
        db.update_balance(user_id, win)

    db.add_game_result(user_id, 'roulette', bet, win, f"{result_num} ({color})")

    new_balance = db.get_balance(user_id)
    profit = win - bet

    await update.message.reply_text(
        f"{desc}\n\n"
        f"💰 Баланс: {new_balance} ({profit:+d})"
    )