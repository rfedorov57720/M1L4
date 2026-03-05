import telebot
from pokemon_class import Pokemon
from random import randint

bot = telebot.TeleBot("YOUR_TOKEN")

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username not in Pokemon.pokemons:
        Pokemon(message.from_user.username)
        bot.send_message(message.chat.id, "Покемон создан!")
    else:
        bot.send_message(message.chat.id, "У вас уже есть покемон!")
    
    show_pokemon_info(message)

@bot.message_handler(commands=['info'])
def show_pokemon_info(message):
    pokemon = Pokemon.pokemons[message.from_user.username]
    bot.send_message(message.chat.id, pokemon.info())
    bot.send_photo(message.chat.id, pokemon.show_img())

@bot.message_handler(commands=['abilities'])
def show_abilities(message):
    pokemon = Pokemon.pokemons[message.from_user.username]
    bot.send_message(message.chat.id, pokemon.get_abilities_info())

@bot.message_handler(commands=['battle'])
def battle(message):
    pokemon = Pokemon.pokemons[message.from_user.username]
    bot.send_message(message.chat.id, pokemon.battle_cry())

@bot.message_handler(commands=['train'])
def train(message):
    pokemon = Pokemon.pokemons[message.from_user.username]
    exp_gain = randint(10, 50)
    pokemon.gain_experience(exp_gain)
    bot.send_message(message.chat.id, f"Тренировка завершена! Получено {exp_gain} опыта!")
    show_pokemon_info(message)

@bot.message_handler(commands=['attack'])
def attack(message):
    attacker = Pokemon.pokemons[message.from_user.username]
    
    # Находим случайного противника
    opponents = [p for username, p in Pokemon.pokemons.items() 
                if username != message.from_user.username]
    
    if opponents:
        target = opponents[randint(0, len(opponents) - 1)]
        damage = attacker.attack + randint(0, 10)
        actual_damage = target.take_damage(damage)
        
        bot.send_message(message.chat.id, 
                        f"⚔️ {attacker.name} атакует {target.name}!\n"
                        f"Нанесено урона: {actual_damage}")
        
        if target.hp <= 0:
            bot.send_message(message.chat.id, f"🎉 Победа! {target.name} повержен!")
            exp_gain = randint(30, 80)
            attacker.gain_experience(exp_gain)
            target.heal()  # Восстанавливаем побежденного
    else:
        bot.send_message(message.chat.id, "Нет противников для атаки!")

@bot.message_handler(commands=['rename'])
def rename_pokemon(message):
    bot.send_message(message.chat.id, "Отправьте новое имя для вашего покемона:")
    bot.register_next_step_handler(message, process_rename)

def process_rename(message):
    pokemon = Pokemon.pokemons[message.from_user.username]
    pokemon.set_name(message.text)
    bot.send_message(message.chat.id, f"Имя изменено на {pokemon.name}!")

bot.infinity_polling()