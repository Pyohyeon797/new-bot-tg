from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio
from datetime import datetime

TOKEN = "8040321172:AAEju1J_mm3J_TLIIY3SZKYvVbjbOTUrOTo"
ADMIN_CHAT_ID = "-4686601366"  # ID вашей группы (должен начинаться с -100)
ADMIN_LINK = "https://t.me/midav0101"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список городов Узбекистана
UZBEKISTAN_CITIES = [
    "Ташкент",
    "Самарканд",
    "Бухара",
    "Наманган",
    "Андижан",
    "Фергана",
    "Карши",
    "Нукус",
    "Ургенч",
    "Гулистан",
    "Джизак",
    "Термез"
]

# Районы Ташкента
TASHKENT_DISTRICTS = [
    "Мирабадский",
    "Чиланзарский",
    "Юнусабадский",
    "Шайхантахурский",
    "Яшнабадский",
    "Яккасарайский",
    "Бектемирский",
    "Сергелийский",
    "Алмазарский",
    "Учтепинский"
]

# Подключение БД
def get_db():
    conn = sqlite3.connect('kifkif.db')
    return conn

# Инициализация БД
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS cart")  # Удаляем старую таблицу если есть
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        city TEXT,
        district TEXT,
        orders_count INTEGER DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        product_name TEXT,
        price REAL,
        quantity INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        products TEXT,
        total REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
   # Добавляем тестовые товары
    products = [
        ("iPhone 15 Pro", 999.99),
        ("Samsung Galaxy S23", 899.99),
        ("Xiaomi 13T Pro", 799.99),
        ("MacBook Air M2", 1299.99),
        ("iPad Pro 12.9", 1099.99),
        ("Apple Watch Series 9", 399.99),
        ("AirPods Pro 2", 249.99),
        ("PlayStation 5", 499.99),
        ("Xbox Series X", 499.99),
        ("Nintendo Switch OLED", 349.99),
        ("DJI Mini 3 Pro", 759.99),
        ("GoPro Hero 11", 399.99),
        ("Sony WH-1000XM5", 399.99),
        ("Bose QuietComfort 45", 329.99),
        ("LG OLED C3", 1499.99)
    ]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO products (name, price) VALUES (?, ?)", products)
    
    conn.commit()
    conn.close()
    
# Главное меню
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль"), KeyboardButton(text="Витрина")],
            [KeyboardButton(text="Правила"), KeyboardButton(text="Контакты"), KeyboardButton(text="Корзина")]
        ],
        resize_keyboard=True
    )

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "не указан"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

    # Создаем клавиатуру с городами
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Ташкент"), KeyboardButton(text="Самарканд")],
        [KeyboardButton(text="Бухара"), KeyboardButton(text="Наманган")],
        [KeyboardButton(text="Андижан"), KeyboardButton(text="Фергана")],
        [KeyboardButton(text="Карши"), KeyboardButton(text="Нукус")],
        [KeyboardButton(text="Ургенч"), KeyboardButton(text="Гулистан")],
        [KeyboardButton(text="Джизак"), KeyboardButton(text="Термез")]
    ])

    await message.answer(
        "🚀 Добро пожаловать в наш магазин!\n\n"
        "Выберите ваш город из списка ниже:",
        reply_markup=keyboard
    )

# Обработка выбора города
@dp.message(F.text.in_(UZBEKISTAN_CITIES))
async def process_city(message: types.Message):
    user_id = message.from_user.id
    city = message.text

    conn = get_db()
    cursor = conn.cursor()
    
    if city == "Ташкент":
        # Для Ташкента показываем районы
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text="Мирабадский"), KeyboardButton(text="Чиланзарский")],
            [KeyboardButton(text="Юнусабадский"), KeyboardButton(text="Шайхантахурский")],
            [KeyboardButton(text="Яшнабадский"), KeyboardButton(text="Яккасарайский")],
            [KeyboardButton(text="Бектемирский"), KeyboardButton(text="Сергелийский")],
            [KeyboardButton(text="Алмазарский"), KeyboardButton(text="Учтепинский")]
        ])
        
        await message.answer(
            "Выберите ваш район в Ташкенте:",
            reply_markup=keyboard
        )
    else:
        # Для других городов сразу сохраняем и показываем меню
        cursor.execute("UPDATE users SET city=?, district=NULL WHERE user_id=?", (city, user_id))
        conn.commit()
        await message.answer(
            f"📍 Ваш город: {city}",
            reply_markup=get_main_menu()
        )
    
    conn.close()

# Обработка выбора района (только для Ташкента)
@dp.message(F.text.in_(TASHKENT_DISTRICTS))
async def process_district(message: types.Message):
    user_id = message.from_user.id
    district = message.text

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET city=?, district=? WHERE user_id=?", 
        ("Ташкент", district, user_id)
    )
    conn.commit()
    conn.close()

    await message.answer(
        f"📍 Ваш район: {district}\n"
        "Теперь вы можете делать заказы!",
        reply_markup=get_main_menu()
    )

# Контакты
@dp.message(F.text == "Контакты")
async def show_contacts(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать админу", url=ADMIN_LINK)]
    ])
    await message.answer(
        "📞 Контакты:\n\n"
        "По всем вопросам пиши админу:\n"
        "@midav0101\n\n"
        "Работаем 10:00-22:00",
        reply_markup=kb
    )

# Правила
@dp.message(F.text == "Правила")
async def show_rules(message: types.Message):
    await message.answer(
        "📜 Правила просты:\n\n"
        "1. Оплата - предоплата\n"
        "2. Доставка 1-3 дня\n"
        "3. Гарантия 14 дней\n"
        "4. Возврат при браке\n\n"
        "Все четко и без обмана!"
    )

# Витрина товаров
@dp.message(F.text == "Витрина")
async def show_products(message: types.Message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, price FROM products")
    products = cursor.fetchall()
    conn.close()

    if not products:
        await message.answer("🛒 Витрина пуста")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for product_id, name, price in products:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(
                text=f"{name} - {price} сум",
                callback_data=f"add_{product_id}"
            )]
        )
    
    kb.inline_keyboard.append(
        [InlineKeyboardButton(
            text="❌ Закрыть",
            callback_data="close_products"
        )]
    )

    await message.answer(
        "🎁 Выберите товар:",
        reply_markup=kb
    )

# Обработчик выбора товара
@dp.callback_query(F.data.startswith("add_"))
async def add_product_handler(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    
    # Получаем информацию о товаре
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE product_id=?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        await callback.answer("❌ Товар не найден")
        return
    
    product_name, price = product
    
    await callback.message.answer(
        f"Введите количество для товара: {product_name}"
    )
    await callback.answer()

    # Ждем ввода количества
    @dp.message(F.from_user.id == callback.from_user.id)
    async def process_quantity(message: types.Message):
        try:
            quantity = int(message.text)
            if quantity <= 0:
                await message.answer("❌ Введите число больше 0!")
                return
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO cart 
                (user_id, product_id, product_name, price, quantity) 
                VALUES (?, ?, ?, ?, ?)''',
                (callback.from_user.id, product_id, product_name, price, quantity)
            )
            conn.commit()
            conn.close()
            
            await message.answer("✅ Товар добавлен в корзину!")
        except ValueError:
            await message.answer("❌ Введите число!")
        
        # Удаляем временный обработчик
        dp.message_handlers.unregister(process_quantity)

# Профиль
@dp.message(F.text == "Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, city, district, orders_count FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    conn.close()

    username = data[0] if data else "не указан"
    city = data[1] if data else "не выбран"
    district = data[2] if data and data[2] else "не выбран"
    orders = data[3] if data else 0

    await message.answer(
        f"👤 Твой профиль:\n\n"
        f"📛 Ник: @{username}\n"
        f"📍 Город: {city}\n"
        f"🏠 Район: {district}\n"
        f"🛍 Заказов: {orders}\n"
        f"🆔 Твой ID: {user_id}"
    )

# Корзина
@dp.message(F.text == "Корзина")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT product_name, price, quantity 
    FROM cart 
    WHERE user_id = ?
    ''', (user_id,))
    
    items = cursor.fetchall()
    conn.close()
    
    if not items:
        await message.answer("🛒 Корзина пуста")
        return
    
    total = 0
    cart_text = "🛒 Ваша корзина:\n\n"
    for name, price, quantity in items:
        item_sum = price * quantity
        cart_text += f"{name} x{quantity} = {item_sum:,} сум\n"
        total += item_sum
    
    cart_text += f"\n💵 Итого: {total:,} сум"
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Очистить корзину"), KeyboardButton(text="✅ Оформить заказ")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(cart_text, reply_markup=keyboard)

# Очистка корзины
@dp.message(F.text == "❌ Очистить корзину")
async def clear_cart(message: types.Message):
    user_id = message.from_user.id
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    await message.answer("🗑 Корзина очищена!", reply_markup=get_main_menu())

# Оформление заказа
@dp.message(F.text == "✅ Оформить заказ")
async def checkout(message: types.Message):
    user_id = message.from_user.id
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Получаем данные корзины
    cursor.execute('''
    SELECT product_name, price, quantity 
    FROM cart 
    WHERE user_id = ?
    ''', (user_id,))
    
    items = cursor.fetchall()
    
    if not items:
        await message.answer("❌ Корзина пуста!")
        conn.close()
        return
    
    # Формируем текст заказа
    total = 0
    order_text = "📦 Новый заказ!\n\n"
    order_text += f"👤 Покупатель: @{message.from_user.username} (ID: {user_id})\n"
    
    # Получаем город и район
    cursor.execute("SELECT city, district FROM users WHERE user_id=?", (user_id,))
    city_data = cursor.fetchone()
    city = city_data[0] if city_data else "Не указан"
    district = city_data[1] if city_data and city_data[1] else ""
    
    if district:
        order_text += f"📍 Город: {city}, район: {district}\n"
    else:
        order_text += f"📍 Город: {city}\n"
    
    order_text += "\n🛒 Состав заказа:\n"
    
    for name, price, quantity in items:
        item_sum = price * quantity
        order_text += f"- {name} x{quantity} = {item_sum:,} сум\n"
        total += item_sum
    
    order_text += f"\n💵 Итого: {total:,} сум\n"
    order_text += f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    # Сохраняем заказ в БД
    cursor.execute(
        "INSERT INTO orders (user_id, products, total, date) VALUES (?, ?, ?, ?)",
        (user_id, order_text, total, datetime.now().strftime('%d.%m.%Y %H:%M')))
    
    # Увеличиваем счетчик заказов
    cursor.execute("UPDATE users SET orders_count = orders_count + 1 WHERE user_id = ?", (user_id,))
    
    # Очищаем корзину
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    # Уведомляем пользователя
    await message.answer(
        "🚀 Заказ оформлен! Ожидайте связи.",
        reply_markup=get_main_menu()
    )
    
    # Отправляем уведомление в группу
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=order_text
        )
    except Exception as e:
        print(f"Ошибка при отправке в группу: {e}")

# Запуск бота
async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())