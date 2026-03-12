import telebot
from random import randint
from config import token 
from logic import Pokemon, Wizard,Fighter
from telebot import types

bot = telebot.TeleBot(token)

Pokemon.pokemons = {}

def create_main_keyboard():
    """Создание основной клавиатуры с командами"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        types.KeyboardButton("🎮 Создать покемона (/go)"),
        types.KeyboardButton("⚔️ Атаковать (/attack)"),
        types.KeyboardButton("❤️ Лечение (/heal)"),
        types.KeyboardButton("📊 Моя статистика (/info)"),
        types.KeyboardButton("👥 Игроки (/players)"),
        types.KeyboardButton("❓ Помощь (/help)")
    ]
    keyboard.add(*buttons)
    return keyboard

def create_attack_keyboard():
    """Создание клавиатуры для атаки"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Создаем кнопки для каждого игрока с покемоном
    attack_buttons = []
    for username, pokemon in Pokemon.pokemons.items():
        if pokemon.health > 0:  # Только живые покемоны
            button = types.InlineKeyboardButton(
                f"⚔️ @{username} ({pokemon.name})", 
                callback_data=f"attack_{username}"
            )
            attack_buttons.append(button)
    
    # Добавляем кнопки по 2 в ряд
    for i in range(0, len(attack_buttons), 2):
        if i + 1 < len(attack_buttons):
            keyboard.row(attack_buttons[i], attack_buttons[i + 1])
        else:
            keyboard.row(attack_buttons[i])
    
    keyboard.row(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_attack"))
    return keyboard

def create_pokemon_choice_keyboard():
    """Создание клавиатуры для выбора типа покемона при создании"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("🐾 Обычный", callback_data="create_normal"),
        types.InlineKeyboardButton("🧙 Волшебник", callback_data="create_wizard"),
        types.InlineKeyboardButton("⚔️ Боец", callback_data="create_fighter"),
        types.InlineKeyboardButton("🎲 Случайно", callback_data="create_random")
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветственное сообщение с инструкцией"""
    welcome_text = """
    🎮 Добро пожаловать в игру Покемоны! 🎮
    
    Доступные команды:
    /go - Создать нового покемона
    /attack - Атаковать другого игрока (ответь на его сообщение)
    /heal - Восстановить здоровье своего покемона
    /info - Информация о твоем покемоне
    /players - Список всех игроков с покемонами
    /help - Показать это сообщение
    
    Чтобы атаковать, просто нажми на кнопку и выбери цель!
    """
    
    bot.send_message(
        message.chat.id, 
        welcome_text,
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(commands=['go'])
def start(message):
    """Создание покемона при старте"""
    username = message.from_user.username
    
    if username not in Pokemon.pokemons.keys():
        # Показываем клавиатуру с выбором типа покемона
        bot.send_message(
            message.chat.id,
            "Выбери тип покемона:",
            reply_markup=create_pokemon_choice_keyboard()
        )
    else:
        bot.reply_to(
            message, 
            "Ты уже создал себе покемона!",
            reply_markup=create_main_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('create_'))
def handle_pokemon_creation(call):
    """Обработка создания покемона через inline кнопки"""
    username = call.from_user.username
    
    if username in Pokemon.pokemons.keys():
        bot.answer_callback_query(call.id, "У тебя уже есть покемон!")
        return
    
    choice = call.data.replace('create_', '')
    
    if choice == 'normal':
        pokemon = Pokemon(username)
    elif choice == 'wizard':
        pokemon = Wizard(username)
    elif choice == 'fighter':
        pokemon = Fighter(username)
    else:  # random
        chance = randint(1, 5)
        if chance == 1:
            pokemon = Wizard(username)
        elif chance == 2:
            pokemon = Fighter(username)
        else:
            pokemon = Pokemon(username)
    
    # Отправляем сообщение с информацией о созданном покемоне
    bot.edit_message_text(
        f"✅ Покемон создан!\n\n{pokemon.info()}",
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_photo(call.message.chat.id, pokemon.show_img())
    
    # Обновляем основную клавиатуру
    bot.send_message(
        call.message.chat.id,
        "Что делаем дальше?",
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(commands=['attack'])
def attack_pok(message):
    """Атака на покемона другого игрока"""
    username = message.from_user.username
    
    # Проверяем, есть ли у атакующего покемон
    if username not in Pokemon.pokemons.keys():
        bot.send_message(
            message.chat.id,
            "❌ У тебя нет покемона! Сначала создай его командой /go",
            reply_markup=create_main_keyboard()
        )
        return
    
    # Проверяем, жив ли покемон атакующего
    if Pokemon.pokemons[username].health <= 0:
        bot.send_message(
            message.chat.id,
            "❌ Твой покемон без сознания! Используй /heal для лечения",
            reply_markup=create_main_keyboard()
        )
        return
    
    # Если есть хотя бы одна цель для атаки
    if len([p for p in Pokemon.pokemons.values() if p.health > 0]) > 1:
        bot.send_message(
            message.chat.id,
            "Выбери противника для атаки:",
            reply_markup=create_attack_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Нет доступных противников для атаки!",
            reply_markup=create_main_keyboard()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('attack_'))
def handle_attack(call):
    """Обработка атаки через inline кнопки"""
    if call.data == "cancel_attack":
        bot.edit_message_text(
            "Атака отменена",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id, "Атака отменена")
        return
    
    attacker_name = call.from_user.username
    target_name = call.data.replace('attack_', '')
    
    # Проверки
    if attacker_name not in Pokemon.pokemons.keys():
        bot.answer_callback_query(call.id, "У тебя нет покемона!")
        return
    
    if target_name not in Pokemon.pokemons.keys():
        bot.answer_callback_query(call.id, "Цель не найдена!")
        return
    
    if attacker_name == target_name:
        bot.answer_callback_query(call.id, "Нельзя атаковать самого себя!")
        return
    
    attacker = Pokemon.pokemons[attacker_name]
    target = Pokemon.pokemons[target_name]
    
    if attacker.health <= 0:
        bot.answer_callback_query(call.id, "Твой покемон без сознания!")
        return
    
    if target.health <= 0:
        bot.answer_callback_query(call.id, "Цель уже побеждена!")
        return
    
    # Проводим атаку
    result = attacker.attack(target)
    
    # Формируем сообщение о результате
    attack_message = f"⚔️ РЕЗУЛЬТАТ БИТВЫ ⚔️\n\n{result}"
    
    if target.health <= 0:
        attack_message += f"\n\n🏆 {attacker.name} ПОБЕДИЛ! 🏆"
    
    # Обновляем сообщение с результатом
    bot.edit_message_text(
        attack_message,
        call.message.chat.id,
        call.message.message_id
    )
    
    # Добавляем кнопку для повторной атаки
    if target.health > 0 and attacker.health > 0:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("⚔️ Атаковать снова", callback_data=f"attack_{target_name}")
        )
        bot.send_message(
            call.message.chat.id,
            "Хочешь атаковать снова?",
            reply_markup=keyboard
        )

@bot.message_handler(commands=['heal'])
def heal_pokemon(message):
    """Восстановление здоровья покемона"""
    username = message.from_user.username
    
    if username in Pokemon.pokemons.keys():
        pokemon = Pokemon.pokemons[username]
        
        # Изменяем условие с health < max_health на hp < max_hp
        if pokemon.hp < pokemon.max_hp:
            pokemon.heal()  # Используем метод heal() из класса
            bot.send_message(
                message.chat.id,
                f"✨ {pokemon.name} полностью восстановил здоровье!\n\n{pokemon.info()}",
                reply_markup=create_main_keyboard()
            )
        else:
            bot.send_message(
                message.chat.id,
                f"{pokemon.name} уже в полном здравии!",
                reply_markup=create_main_keyboard()
            )
    else:
        bot.send_message(
            message.chat.id,
            "У тебя нет покемона. Сначала создай его командой /go",
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(commands=['info'])
def show_info(message):
    """Показать информацию о своем покемоне"""
    username = message.from_user.username
    
    if username in Pokemon.pokemons.keys():
        pokemon = Pokemon.pokemons[username]
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.send_message(
            message.chat.id,
            "У тебя нет покемона. Создай его командой /go",
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(commands=['players'])
def show_players(message):
    """Показать всех игроков с покемонами"""
    if Pokemon.pokemons:
        players_list = "👥 СПИСОК ИГРОКОВ 👥\n\n"
        for username, pokemon in Pokemon.pokemons.items():
            health_status = f"❤️ {pokemon.health}/{pokemon.max_health}"
            if pokemon.health <= 0:
                health_status = "💀 Без сознания"
            
            if isinstance(pokemon, Wizard):
                pokemon_type = "🧙 Волшебник"
            elif isinstance(pokemon, Fighter):
                pokemon_type = "⚔️ Боец"
            else:
                pokemon_type = "🐾 Обычный"
            
            players_list += f"@{username}: {pokemon.name} ({pokemon_type}) - {health_status}\n"
        
        bot.send_message(message.chat.id, players_list, reply_markup=create_main_keyboard())
    else:
        bot.send_message(
            message.chat.id,
            "Пока нет ни одного покемона",
            reply_markup=create_main_keyboard()
        )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработка текстовых сообщений и кнопок"""
    text = message.text
    
    if text == "🎮 Создать покемона (/go)":
        start(message)
    elif text == "⚔️ Атаковать (/attack)":
        attack_pok(message)
    elif text == "❤️ Лечение (/heal)":
        heal_pokemon(message)
    elif text == "📊 Моя статистика (/info)":
        show_info(message)
    elif text == "👥 Игроки (/players)":
        show_players(message)
    elif text == "❓ Помощь (/help)":
        send_welcome(message)

if __name__ == '__main__':
    print("Бот запущен с интерактивными кнопками...")
    
    # Тестирование классов
    wizard = Wizard("test_wizard")
    fighter = Fighter("test_fighter")
    
    print(wizard.info())
    print()
    print(fighter.info())
    print()
    print(fighter.attack(wizard))
    
    bot.infinity_polling()