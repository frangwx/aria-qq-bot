from typing import List, Dict, Optional
from dataclasses import dataclass
import httpx

from src.utils import get_logger

logger = get_logger()


@dataclass
class Character:
    name: str
    element: str
    faction: str
    rarity: int
    weapon_type: str
    description: str
    
    def to_message(self) -> str:
        stars = "★" * self.rarity
        return f"""【{self.name}】
⭐ {stars}
🔮 属性: {self.element}
🏢 阵营: {self.faction}
⚔️ 武器: {self.weapon_type}
📝 {self.description}"""


@dataclass
class Material:
    name: str
    type: str
    source: str
    description: str
    
    def to_message(self) -> str:
        return f"""【{self.name}】
📦 类型: {self.type}
📍 获取: {self.source}
📝 {self.description}"""


class GameDataService:
    CHARACTERS = {
        "艾莲": Character("艾莲", "冰", "维多利亚家政", 5, "斩击", "维多利亚家政的清扫员，以高效著称的冷酷少女。"),
        "莱卡恩": Character("莱卡恩", "物理", "维多利亚家政", 5, "打击", "维多利亚家政的管家，举止优雅的狼人。"),
        "丽娜": Character("丽娜", "电", "维多利亚家政", 5, "斩击", "维多利亚家政的女仆长，温柔但实力强大。"),
        "珂蕾妲": Character("珂蕾妲", "火", "白祇重工", 5, "打击", "白祇重工的社长，天才机械师少女。"),
        "格蕾丝": Character("格蕾丝", "电", "白祇重工", 5, "斩击", "白祇重工的工程师，对机械有着狂热的喜爱。"),
        "猫又": Character("猫又", "物理", "狡兔屋", 5, "斩击", "狡兔屋的代理人，猫耳少女。"),
        "妮可": Character("妮可", "以太", "狡兔屋", 4, "打击", "狡兔屋的老板，精打细算的少女。"),
        "安比": Character("安比", "电", "狡兔屋", 4, "斩击", "狡兔屋的成员，沉默寡言的少女。"),
        "比利": Character("比利", "物理", "狡兔屋", 4, "射击", "狡兔屋的成员，双枪少年。"),
        "朱鸢": Character("朱鸢", "以太", "对空洞特别行动部", 5, "射击", "对空洞特别行动部的精英探员。"),
        "青衣": Character("青衣", "电", "对空洞特别行动部", 4, "打击", "对空洞特别行动部的探员。"),
        "简": Character("简", "物理", "对空洞特别行动部", 5, "斩击", "对空洞特别行动部的王牌探员。"),
        "珂珂": Character("珂珂", "冰", "对空洞特别行动部", 4, "斩击", "对空洞特别行动部的探员。"),
        "11号": Character("11号", "火", "对空洞特别行动部", 5, "打击", "对空洞特别行动部的精英探员，代号11号。"),
        "苍角": Character("苍角", "冰", "对空洞特别行动部", 5, "斩击", "对空洞特别行动部的探员，使用冰之剑技。"),
        "雅": Character("雅", "冰", "对空洞特别行动部", 5, "斩击", "对空洞特别行动部的最强探员。"),
    }
    
    MATERIALS = {
        "丁尼": Material("丁尼", "货币", "日常任务、活动奖励", "游戏内主要货币，用于各种升级和购买。"),
        "菲林": Material("菲林", "高级货币", "充值、活动奖励", "高级货币，用于抽取角色和武器。"),
        "以太": Material("以太", "素材", "空洞探索、副本", "用于角色升级的基础素材。"),
        "冰晶": Material("冰晶", "元素素材", "冰属性空洞", "冰属性角色突破素材。"),
        "炎核": Material("炎核", "元素素材", "火属性空洞", "火属性角色突破素材。"),
        "雷核": Material("雷核", "元素素材", "电属性空洞", "电属性角色突破素材。"),
        "以太核": Material("以太核", "元素素材", "以太空洞", "以太属性角色突破素材。"),
        "物理核": Material("物理核", "元素素材", "物理空洞", "物理属性角色突破素材。"),
        "音擎": Material("音擎", "武器", "抽卡、活动", "角色的武器，提供属性加成和特殊效果。"),
        "驱动盘": Material("驱动盘", "装备", "副本、活动", "角色的装备，提供属性加成。"),
    }
    
    async def search_character(self, name: str) -> Optional[Character]:
        name = name.strip()
        for char_name, char in self.CHARACTERS.items():
            if name in char_name or char_name in name:
                return char
        return None
    
    async def list_characters(self, element: str = None, rarity: int = None) -> List[Character]:
        chars = list(self.CHARACTERS.values())
        
        if element:
            chars = [c for c in chars if c.element == element]
        if rarity:
            chars = [c for c in chars if c.rarity == rarity]
        
        return chars
    
    async def search_material(self, name: str) -> Optional[Material]:
        name = name.strip()
        for mat_name, mat in self.MATERIALS.items():
            if name in mat_name or mat_name in name:
                return mat
        return None
    
    async def list_materials(self, mat_type: str = None) -> List[Material]:
        mats = list(self.MATERIALS.values())
        
        if mat_type:
            mats = [m for m in mats if m.type == mat_type]
        
        return mats
    
    def get_character_list_message(self, chars: List[Character]) -> str:
        if not chars:
            return "未找到符合条件的角色"
        
        lines = ["【角色列表】", ""]
        for char in chars:
            stars = "★" * char.rarity
            lines.append(f"{char.name} | {char.element} | {stars}")
        
        return "\n".join(lines)
    
    def get_material_list_message(self, mats: List[Material]) -> str:
        if not mats:
            return "未找到符合条件的材料"
        
        lines = ["【材料列表】", ""]
        for mat in mats:
            lines.append(f"{mat.name} | {mat.type}")
        
        return "\n".join(lines)


game_data = GameDataService()
