import sqlite3
import os
from datetime import datetime, timedelta
from config import START_BALANCE, DAILY_BONUS

# Путь к базе данных (всегда рядом с файлом)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'casino_bot.db')

def get_connection():
    """Получить соединение с БД"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Инициализация базы данных"""
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT {START_BALANCE},
            total_games INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            total_losses INTEGER DEFAULT 0,
            last_daily TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # История игр
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_type TEXT,
            bet_amount INTEGER,
            win_amount INTEGER,
            result TEXT,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()

def register_user(user_id, username):
    """Регистрация нового пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
    ''', (user_id, username))
    conn.commit()
    conn.close()

def get_balance(user_id):
    """Получить баланс пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_balance(user_id, amount):
    """Обновить баланс (amount может быть отрицательным)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET balance = balance + ?
        WHERE user_id = ?
    ''', (amount, user_id))
    conn.commit()
    conn.close()

def add_game_result(user_id, game_type, bet, win, result):
    """Добавить результат игры"""
    conn = get_connection()
    cursor = conn.cursor()

    # Записываем историю
    cursor.execute('''
        INSERT INTO game_history (user_id, game_type, bet_amount, win_amount, result)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, game_type, bet, win, result))

    # Обновляем статистику
    is_win = 1 if win > bet else 0
    cursor.execute('''
        UPDATE users
        SET total_games = total_games + 1,
            total_wins = total_wins + ?,
            total_losses = total_losses + ?
        WHERE user_id = ?
    ''', (is_win, 1 - is_win, user_id))

    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Получить статистику пользователя"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT balance, total_games, total_wins, total_losses
        FROM users
        WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 0, 0, 0)

def get_top_players(limit=10):
    """Получить топ игроков по балансу"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, balance, total_games, total_wins
        FROM users
        ORDER BY balance DESC
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def claim_daily_bonus(user_id):
    """Получить ежедневный бонус"""
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем последний бонус
    cursor.execute('SELECT last_daily FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if result and result[0]:
        last_daily = datetime.fromisoformat(result[0])
        if datetime.now() - last_daily < timedelta(days=1):
            conn.close()
            remaining = timedelta(days=1) - (datetime.now() - last_daily)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            return False, f"{hours}ч {minutes}м"

    # Начисляем бонус
    cursor.execute('''
        UPDATE users
        SET balance = balance + ?,
            last_daily = ?
        WHERE user_id = ?
    ''', (DAILY_BONUS, datetime.now().isoformat(), user_id))

    conn.commit()
    conn.close()
    return True, None