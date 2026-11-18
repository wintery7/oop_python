# 🎮 실습: 상속(IS-A)과 구성(HAS-A)으로 게임 객체 설계하기

# 문제 1. IS-A인가, HAS-A인가?
# 1. Slime ― Monster        : IS-A 
# 2. Character ― HP         : HAS-A 
# 3. Wizard ― Character     : IS-A  
# 4. Character ― Skill      : HAS-A 
# 5. Monster ― GameObject   : IS-A  
# 6. Dragon ― Weapon        : HAS-A
# 7. Character ― Armor      : HAS-A 
# 8. Warrior ― GameObject   : IS-A 


class GameObject:
    def __init__(self, name, x=0, y=0):
        self.name = name
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def info(self):
        return f"{self.name} ({self.x}, {self.y})"


class Monster(GameObject):
    def __init__(self, name, power, x=0, y=0):
        super().__init__(name, x, y)   # name, x, y 는 부모(GameObject)에게 맡김
        self.power = power             # Monster 에만 있는 추가 속성


class Dragon(Monster):
    pass


class Slime(Monster):
    pass


# 문제 3. 구성(HAS-A)으로 캐릭터 완성하기

class HP:
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.current = max_hp

    def damage(self, amount):
        self.current = max(self.current - amount, 0)   # 0 미만으로 내려가지 않음

    def is_alive(self):
        return self.current > 0


class Weapon:
    def __init__(self, name, power):
        self.name = name
        self.power = power


class Skill:
    def __init__(self, name, multiplier):
        self.name = name
        self.multiplier = multiplier


class Armor:
    def __init__(self, name, defense):
        self.name = name
        self.defense = defense


# Character: GameObject 상속(IS-A) + 부품 구성(HAS-A)
class Character(GameObject):
    def __init__(self, name, max_hp, weapon, skill, armor, x=0, y=0):
        super().__init__(name, x, y)
        self.hp = HP(max_hp)     # has-a HP
        self.weapon = weapon     # has-a Weapon
        self.skill = skill       # has-a Skill
        self.armor = armor       # has-a Armor

    def attack(self):
        return self.weapon.power

    def use_skill(self):
        return int(self.weapon.power * self.skill.multiplier)

    def take_damage(self, amount):
        actual = max(amount - self.armor.defense, 0)   # 방어력만큼 줄이되 최소 0
        self.hp.damage(actual)
        return actual

    def change_weapon(self, weapon):
        self.weapon = weapon


# ③ 직업 클래스
class Warrior(Character):
    def __init__(self, name):
        super().__init__(
            name,
            150,
            Weapon("롱소드", 20),
            Skill("강타", 1.5),
            Armor("판금갑옷", 10),
        )


class Wizard(Character):
    def __init__(self, name):
        super().__init__(
            name,
            90,
            Weapon("지팡이", 8),
            Skill("파이어볼", 4.0),
            Armor("로브", 2),
        )


# 실행 코드
if __name__ == "__main__":
    print("=== 문제 2 ===")
    d = Dragon("드래곤", 50)
    d.move(3, 4)
    print(d.info())
    print(isinstance(d, Monster), isinstance(d, GameObject), isinstance(d, Character))

    print("\n=== 문제 3 ===")
    w = Warrior("아서")
    z = Wizard("멀린")

    print(w.attack(), w.use_skill(), z.use_skill())
    print(w.take_damage(25), w.hp.current)
    print(z.take_damage(25), z.hp.current)

    w.change_weapon(Weapon("전투도끼", 30))
    print(w.attack(), w.use_skill())
