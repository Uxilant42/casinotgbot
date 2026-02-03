import random
from config import SLOT_SYMBOLS

def play_slots(bet):
    """
    Игра в слоты
    Возвращает: (результат, выигрыш, описание)
    """
    reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    result_str = " ".join(reels)

    if reels[0] == reels[1] == reels[2]:
        if reels[0] == "7️⃣":
            multiplier = 10
            win = bet * multiplier
            desc = f"🎰 {result_str}\n\n🎉 ДЖЕКПОТ! x{multiplier}"
        elif reels[0] == "💎":
            multiplier = 5
            win = bet * multiplier
            desc = f"🎰 {result_str}\n\n💎 Бриллианты! x{multiplier}"
        else:
            multiplier = 3
            win = bet * multiplier
            desc = f"🎰 {result_str}\n\n✨ Три одинаковых! x{multiplier}"
    elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        multiplier = 2
        win = bet * multiplier
        desc = f"🎰 {result_str}\n\n👍 Два одинаковых! x{multiplier}"
    else:
        win = 0
        desc = f"🎰 {result_str}\n\n😢 Не повезло..."

    return result_str, win, desc

def play_dice(bet, user_choice):
    """
    Игра в кости (больше/меньше 3.5)
    user_choice: 'high' или 'low'
    Возвращает: (результат, выигрыш, описание)
    """
    dice = random.randint(1, 6)

    won = False
    if user_choice == 'high' and dice >= 4:
        won = True
    elif user_choice == 'low' and dice <= 3:
        won = True

    if won:
        win = bet * 2
        desc = f"🎲 Выпало: {dice}\n\n🎉 Вы выиграли! x2"
    else:
        win = 0
        desc = f"🎲 Выпало: {dice}\n\n😢 Вы проиграли..."

    return dice, win, desc

def play_roulette(bet, user_choice):
    """
    Рулетка (красное/черное, четное/нечетное, число)
    user_choice: 'red', 'black', 'even', 'odd', или число (0-36)
    Возвращает: (число, цвет, выигрыш, описание)
    """
    number = random.randint(0, 36)

    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    if number == 0:
        color = 'green'
        color_emoji = '🟢'
    elif number in red_numbers:
        color = 'red'
        color_emoji = '🔴'
    else:
        color = 'black'
        color_emoji = '⚫'

    win = 0
    if isinstance(user_choice, int):
        if number == user_choice:
            win = bet * 36
            desc = f"{color_emoji} Выпало: {number}\n\n🎉 Точное попадание! x36"
        else:
            desc = f"{color_emoji} Выпало: {number}\n\n😢 Не угадали..."
    else:
        if (user_choice == 'red' and color == 'red') or \
           (user_choice == 'black' and color == 'black') or \
           (user_choice == 'even' and number % 2 == 0 and number != 0) or \
           (user_choice == 'odd' and number % 2 == 1):
            win = bet * 2
            desc = f"{color_emoji} Выпало: {number}\n\n🎉 Вы угадали! x2"
        else:
            desc = f"{color_emoji} Выпало: {number}\n\n😢 Не повезло..."

    return number, color, win, desc