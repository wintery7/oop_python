# 🐉 게임 설계 실습: 레드 드래곤 토벌 RPG
#   - 상속(IS-A) : GameObject → Character → Warrior
#                  GameObject → Monster   → Slime / Golem / Dragon
#                  Item       → Weapon / EnhanceStone
#   - 구성(HAS-A): Weapon    has-a Element
#                  Character has-a HP, Level, Inventory, Weapon
#                  Monster   has-a HP, Element, Item(드롭)


# ──────────────────────────────────────────────
# 퀘스트 1. 세계의 기초 만들기 (상속)
# ──────────────────────────────────────────────

class GameObject:
    """모든 게임 객체의 부모"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class HP:
    """체력 부품 (Character, Monster 가 HAS-A 로 가짐)"""

    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.current = max_hp

    def damage(self, amount):
        self.current = max(self.current - amount, 0)   # 0 아래로 내려가지 않음

    def heal_full(self):
        self.current = self.max_hp

    def is_alive(self):
        return self.current > 0

    def __str__(self):
        return f"{self.current}/{self.max_hp}"


class Item(GameObject):
    """모든 아이템의 부모 (아이템도 게임 세계의 객체이므로 GameObject IS-A)"""

    def __init__(self, name):
        super().__init__(name)


# ──────────────────────────────────────────────
# ① 속성 상성 : Weapon has-a Element
#    물 → 불 → 풀 → 물  (화살표 방향으로 강함)
# ──────────────────────────────────────────────

class Element:
    STRONG_AGAINST = {"물": "불", "불": "풀", "풀": "물"}

    def __init__(self, name):
        self.name = name

    def multiplier_against(self, other):
        """내 속성으로 상대 속성을 공격할 때의 배율"""
        if self.STRONG_AGAINST[self.name] == other.name:
            return 2.0          # 상성 우위 (예: 물 → 불)
        if self.STRONG_AGAINST[other.name] == self.name or self.name == other.name:
            return 0.5          # 상성 열위 또는 같은 속성 (예: 불 → 불)
        return 1.0

    def __str__(self):
        return self.name


FIRE = Element("불")
WATER = Element("물")
GRASS = Element("풀")


# ──────────────────────────────────────────────
# ③ 아이템 : Item 상속
# ──────────────────────────────────────────────

class Weapon(Item):
    """무기 IS-A 아이템, 무기 HAS-A 속성"""

    ENHANCE_BONUS = 10

    def __init__(self, name, power, element):
        super().__init__(name)
        self.power = power
        self.element = element      # has-a Element
        self.enhance_level = 0

    def enhance(self):
        self.enhance_level += 1
        self.power += self.ENHANCE_BONUS

    def __str__(self):
        plus = f" +{self.enhance_level}" if self.enhance_level else ""
        return f"{self.name}{plus} (공격력 {self.power}, {self.element})"


class EnhanceStone(Item):
    """강화석: 무기를 강화하는 데 소모되는 아이템"""

    def __init__(self):
        super().__init__("강화석")


# ──────────────────────────────────────────────
# ② 레벨 업 : Character has-a Level
# ──────────────────────────────────────────────

class Level:
    def __init__(self):
        self.value = 1
        self.exp = 0

    def required_exp(self):
        return self.value * 100     # Lv1→2: 100, Lv2→3: 200 ...

    def gain_exp(self, amount):
        """경험치를 얻고, 오른 레벨 수를 반환"""
        self.exp += amount
        level_ups = 0
        while self.exp >= self.required_exp():
            self.exp -= self.required_exp()
            self.value += 1
            level_ups += 1
        return level_ups

    def __str__(self):
        return f"Lv.{self.value} ({self.exp}/{self.required_exp()})"


# ──────────────────────────────────────────────
# ③ 인벤토리 : Character has-a Inventory
# ──────────────────────────────────────────────

class Inventory:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def remove(self, item):
        self.items.remove(item)

    def find(self, item_type):
        """특정 종류(클래스)의 첫 아이템을 찾음, 없으면 None"""
        for item in self.items:
            if isinstance(item, item_type):
                return item
        return None

    def __str__(self):
        return "[" + ", ".join(str(item) for item in self.items) + "]"


# ──────────────────────────────────────────────
# 캐릭터 : GameObject 상속 + 부품 구성
# ──────────────────────────────────────────────

class Character(GameObject):
    LEVEL_UP_HP = 20        # 레벨 업마다 최대 체력 증가량
    LEVEL_UP_POWER = 5      # 레벨 업마다 공격력 보너스

    def __init__(self, name, max_hp, weapon):
        super().__init__(name)
        self.hp = HP(max_hp)            # has-a HP
        self.level = Level()            # has-a Level
        self.inventory = Inventory()    # has-a Inventory
        self.weapon = weapon            # has-a Weapon (속성은 무기를 따라감)

    @property
    def element(self):
        return self.weapon.element

    def attack_power(self):
        return self.weapon.power + (self.level.value - 1) * self.LEVEL_UP_POWER

    def attack(self, target):
        multiplier = self.weapon.element.multiplier_against(target.element)
        damage = int(self.attack_power() * multiplier)
        target.hp.damage(damage)
        return damage, multiplier

    def gain_exp(self, amount):
        level_ups = self.level.gain_exp(amount)
        if level_ups:
            self.hp.max_hp += self.LEVEL_UP_HP * level_ups
            self.hp.heal_full()         # 레벨 업 시 체력 완전 회복
        return level_ups

    def pick_up(self, item):
        self.inventory.add(item)

    def equip(self, weapon):
        """인벤토리의 무기와 현재 무기를 교체"""
        self.inventory.remove(weapon)
        self.inventory.add(self.weapon)
        self.weapon = weapon

    def enhance_weapon(self):
        """강화석 1개를 소모해 현재 무기를 강화"""
        stone = self.inventory.find(EnhanceStone)
        if stone is None:
            return False
        self.inventory.remove(stone)
        self.weapon.enhance()
        return True

    def __str__(self):
        return (f"{self.name} {self.level} HP {self.hp} | 무기: {self.weapon} "
                f"| 인벤토리: {self.inventory}")


class Warrior(Character):
    def __init__(self, name):
        super().__init__(name, 150, Weapon("화염검", 30, FIRE))


# ──────────────────────────────────────────────
# 몬스터 : GameObject 상속 + 부품 구성
#   (몬스터 공격력은 밸런스 표에 없어 임의로 설정)
# ──────────────────────────────────────────────

class Monster(GameObject):
    def __init__(self, name, max_hp, element, exp, power, drop=None):
        super().__init__(name)
        self.hp = HP(max_hp)        # has-a HP
        self.element = element      # has-a Element
        self.exp = exp
        self.power = power
        self.drop = drop            # has-a Item (없으면 None)

    def attack(self, target):
        target.hp.damage(self.power)
        return self.power

    def __str__(self):
        return f"{self.name}({self.element}) HP {self.hp}"


class Slime(Monster):
    def __init__(self):
        super().__init__("슬라임", 40, GRASS, 60, 8, Weapon("물의 창", 25, WATER))


class Golem(Monster):
    def __init__(self):
        super().__init__("골렘", 120, GRASS, 90, 15, EnhanceStone())


class Dragon(Monster):
    def __init__(self):
        super().__init__("레드 드래곤", 300, FIRE, 500, 30)


# ──────────────────────────────────────────────
# 전투
# ──────────────────────────────────────────────

def battle(hero, monster):
    print(f"\n⚔️  {hero.name} vs {monster}")
    while hero.hp.is_alive() and monster.hp.is_alive():
        damage, multiplier = hero.attack(monster)
        note = {2.0: " 효과가 굉장했다!", 0.5: " 효과가 별로인 듯하다..."}.get(multiplier, "")
        print(f"  {hero.name}의 {hero.weapon.name} 공격! {damage} 피해{note} → {monster}")
        if not monster.hp.is_alive():
            break
        hp_damage = monster.attack(hero)
        print(f"  {monster.name}의 반격! {hp_damage} 피해 → {hero.name} HP {hero.hp}")

    if hero.hp.is_alive():
        print(f"🏆 {monster.name} 처치! 경험치 +{monster.exp}")
        if hero.gain_exp(monster.exp):
            print(f"🎉 레벨 업! {hero.level}, 최대 HP {hero.hp.max_hp}, 체력 완전 회복")
        if monster.drop:
            hero.pick_up(monster.drop)
            print(f"🎁 {monster.drop} 획득!")
        return True

    print(f"💀 {hero.name}이(가) 쓰러졌다...")
    return False


# 실행 코드
if __name__ == "__main__":
    print("=== 퀘스트 1. 세계의 기초 ===")
    hp = HP(100)
    hp.damage(130)
    print(hp, hp.is_alive())        # 0/100 False (0 아래로 내려가지 않음)
    hp.heal_full()
    print(hp, hp.is_alive())        # 100/100 True
    print(isinstance(Weapon("검", 10, FIRE), Item), isinstance(Item("포션"), GameObject))

    print("\n=== 속성 상성 ===")
    print("불 → 풀:", FIRE.multiplier_against(GRASS))    # 2.0
    print("불 → 불:", FIRE.multiplier_against(FIRE))     # 0.5
    print("물 → 불:", WATER.multiplier_against(FIRE))    # 2.0

    print("\n=== 실패 루트: 화염검 그대로 드래곤에게 도전 ===")
    battle(Warrior("아서"), Dragon())

    print("\n=== 정석 루트: 성장 → 무기 교체 → 강화 → 보스전 ===")
    arthur = Warrior("아서")
    print(arthur)
    battle(arthur, Slime())
    battle(arthur, Golem())

    print("\n🔄 장비 교체 & 강화")
    arthur.equip(arthur.inventory.find(Weapon))      # 화염검 → 물의 창
    arthur.enhance_weapon()                          # 강화석 소모
    print(arthur)

    battle(arthur, Dragon())
    print("\n" + str(arthur))
