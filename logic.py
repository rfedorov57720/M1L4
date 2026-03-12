from random import randint
import requests

class Pokemon:
    pokemons = {}
    
    def __init__(self, pokemon_trainer):
        self.pokemon_trainer = pokemon_trainer
        self.pokemon_number = randint(1, 1000)
        self.name = self.get_name()
        self.img = self.get_img()
        self.hp = randint(200, 400)
        self.power = randint(30, 60)
        self.defense = self.get_defense()  # теперь метод существует
        self.type = self.get_types()
        self.abilities = self.get_abilities()
        self.experience = 0
        self.level = 1
        
        Pokemon.pokemons[pokemon_trainer] = self
    
    # Метод для получения базовой информации о покемоне
    def get_pokemon_data(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_name(self):
        data = self.get_pokemon_data()
        if data:
            return data['name'].capitalize()
        return "Pikachu"
    
    def get_img(self):
        data = self.get_pokemon_data()
        if data:
            return data['sprites']['other']['official-artwork']['front_default']
        return "https://static.wikia.nocookie.net/pokemon/images/0/0d/025Pikachu.png"
    
    def get_defense(self):
        """Получение значения защиты покемона"""
        data = self.get_pokemon_data()
        if data and 'stats' in data:
            return data['stats'][2]['base_stat']
        return randint(30, 80)
    
    def get_types(self):
        """Получение типов покемона"""
        data = self.get_pokemon_data()
        if data and 'types' in data:
            types = [t['type']['name'].capitalize() for t in data['types']]
            return ', '.join(types)
        return "Unknown"
    
    def get_abilities(self):
        """Получение способностей покемона"""
        data = self.get_pokemon_data()
        if data and 'abilities' in data:
            abilities = [a['ability']['name'].replace('-', ' ').capitalize() 
                        for a in data['abilities']]
            return abilities
        return ["Unknown"]
    
    def attack(self, enemy):
        if isinstance(enemy, Wizard):
            chance = randint(1, 5)
            if chance == 1:
                return "Покемон-волшебник применил щит в сражение"
        if enemy.hp > self.power:
            enemy.hp -= self.power
            return f"Сражение @{self.pokemon_trainer} с @{enemy.pokemon_trainer}"
        else:
            enemy.hp = 0
            return f"Победа @{self.pokemon_trainer} над @{enemy.pokemon_trainer}! "
    
    def gain_experience(self, exp_points):
        self.experience += exp_points
        # Простая система уровней
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1
            self.level_up()
    
    def level_up(self):
        """Повышение характеристик при повышении уровня"""
        self.hp += randint(5, 10)
        self.power += randint(2, 5)
        self.defense += randint(2, 5)
    
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense // 4)
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self):
        """Восстановление HP"""
        self.hp = randint(200, 400)  # Возвращаем к случайному значению
    
    def info(self):
        return f"""
Имя твоего покемона: {self.name}
HP: {self.hp}
Атака: {self.power}
Защита: {self.defense}
Тип: {self.type}
Уровень: {self.level}
Опыт: {self.experience}"""
    
    def show_img(self):
        return self.img
    
    def get_abilities_info(self):
        abilities_text = "Способности:\n"
        for i, ability in enumerate(self.abilities, 1):
            abilities_text += f"{i}. {ability}\n"
        return abilities_text
    
    def battle_cry(self):
        """Издает боевой клич"""
        return f"{self.name.upper()}!!! {self.name} использует атаку!"
    
    def __str__(self):
        return self.info()


class Wizard(Pokemon):
    def attack(self, enemy):
        return super().attack(enemy)


class Fighter(Pokemon):
    def attack(self, enemy):
        super_power = randint(5, 15)
        self.power += super_power
        result = super().attack(enemy)
        self.power -= super_power
        return result + f"\nБоец применил супер-атаку силой: {super_power}"