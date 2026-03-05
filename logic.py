from random import randint
import requests

class Pokemon:
    pokemons = {}
    
    def __init__(self, pokemon_trainer):
        self.pokemon_trainer = pokemon_trainer
        self.pokemon_number = randint(1, 898)  # Уменьшил до актуального количества покемонов
        self.name = self.get_name()
        self.img = self.get_img()
        self.hp = self.get_hp()
        self.attack = self.get_attack()
        self.defense = self.get_defense()
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
    
    def get_hp(self):
        data = self.get_pokemon_data()
        if data:
            return data['stats'][0]['base_stat']
        return randint(50, 100)
    
    def get_attack(self):
        data = self.get_pokemon_data()
        if data:
            return data['stats'][1]['base_stat']
        return randint(30, 80)
    
    def get_defense(self):
        data = self.get_pokemon_data()
        if data:
            return data['stats'][2]['base_stat']
        return randint(30, 80)
    
    def get_types(self):
        data = self.get_pokemon_data()
        if data:
            types = [t['type']['name'].capitalize() for t in data['types']]
            return ', '.join(types)
        return "Unknown"
    
    def get_abilities(self):
        data = self.get_pokemon_data()
        if data:
            abilities = [a['ability']['name'].replace('-', ' ').capitalize() 
                        for a in data['abilities']]
            return abilities
        return ["Unknown"]
    
    # Методы для изменения свойств
    def set_name(self, new_name):
        self.name = new_name.capitalize()
    
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
        self.attack += randint(2, 5)
        self.defense += randint(2, 5)
    
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense // 4)
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self):
        """Восстановление HP"""
        self.hp = self.get_hp()  # Возвращаем к базовому значению
    
    # Методы для получения информации
    def info(self):
        return f"""📊 Имя: {self.name}
❤️ HP: {self.hp}
⚔️ Атака: {self.attack}
🛡️ Защита: {self.defense}
📚 Тип: {self.type}
⭐ Уровень: {self.level}
✨ Опыт: {self.experience}"""
    
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