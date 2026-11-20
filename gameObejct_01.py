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


# 문제 4. 잘못된 설계 고치기
#
# 1) 어색한 이유
#    "캐릭터는 무기다(IS-A)"는 말이 안 되고 "캐릭터는 무기를 갖는다(HAS-A)"가 맞는 관계인데,
#    상속을 써서 캐릭터를 무기의 한 종류로 만들어 버렸다.
#
# 2) 무기를 바꾸고 싶을 때의 문제점
#    무기가 따로 있는 객체가 아니라 캐릭터 자신(부모 클래스)이라서, 게임 도중에 다른 무기 객체로 갈아 끼울 수 없다.
#    self.power 숫자만 직접 고칠 수 있을 뿐, 무기 이름처럼 무기가 가진 다른 정보는 함께 바뀌지 않는다.
#    새 무기 종류(활, 지팡이 등)를 쓰려면 Character 의 부모 클래스를 바꿔야 하는데, 부모는 클래스를 정의할 때 정해져 실행 중에 바꿀 수 없다.
#
# 3) 구성(HAS-A)으로 고친 코드
#    → 위의 Character 클래스가 바로 이 방식이다. 핵심만 줄이면 아래와 같다.
#
#    class Weapon:
#        def __init__(self, name, power):
#            self.name = name
#            self.power = power
#
#    class Character:
#        def __init__(self, name, weapon):
#            self.name = name
#            self.weapon = weapon          # 상속 대신 무기를 "속성으로 가짐"
#
#        def change_weapon(self, weapon):  # 실행 중에도 무기 교체 가능
#            self.weapon = weapon
#
#    c = Character("아서", Weapon("롱소드", 20))
#    c.change_weapon(Weapon("전투도끼", 30))


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
