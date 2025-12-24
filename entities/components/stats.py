class Stat:
    """属性容器：支持基础值、加法加成、百分比加成"""

    def __init__(self, base_value):
        self.base_value = base_value
        self.flat_modifier = 0
        self.percent_modifier = 0

    @property
    def value(self):
        # 工业标准公式：最终值 = (基础 + 固定加成) * (1 + 百分比加成)
        return (self.base_value + self.flat_modifier) * (1 + self.percent_modifier)


class StatsComponent:
    def __init__(self, config):
        # 基础属性
        self.health = Stat(config.get('health', 100))
        self.max_health = Stat(config.get('health', 100))
        self.move_speed = Stat(config.get('move_speed', 350))

        # 战斗属性（冗余设计：哪怕现在不用，也先预留位置）
        self.damage_mult = Stat(1.0)  # 伤害倍率
        self.attack_area = Stat(1.0)  # 攻击范围倍率
        self.cooldown_reduction = Stat(0.0)  # 冷却缩减
        self.crit_rate = Stat(0.05)  # 暴击率
        self.crit_dmg = Stat(1.5)  # 暴击伤害

        # 实用属性
        self.pickup_range = Stat(120)  # 磁吸范围
        self.luck = Stat(1.0)  # 幸运
        self.exp_gain = Stat(1.0)  # 经验获取率

    def add_modifier(self, stat_name, val, is_percent=True):
        """为特定属性添加加成"""
        stat = getattr(self, stat_name, None)
        if stat:
            if is_percent:
                stat.percent_modifier += val
            else:
                stat.flat_modifier += val