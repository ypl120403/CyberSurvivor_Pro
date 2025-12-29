class Stat:
    """
    属性容器：支持基础值、加法加成、百分比加成。
    一劳永逸点：自动处理非法输入，提供简洁的数值访问。
    """

    def __init__(self, base_value):
        try:
            self.base_value = float(base_value)
        except (ValueError, TypeError):
            self.base_value = 0.0

        self.flat_modifier = 0.0
        self.percent_modifier = 0.0

    @property
    def value(self):
        """核心公式：最终值 = (基础 + 平加) * (1 + 百分比)"""
        return (self.base_value + self.flat_modifier) * (1 + self.percent_modifier)

    def reset_modifiers(self):
        """重置所有加成（用于洗点或特殊逻辑）"""
        self.flat_modifier = 0.0
        self.percent_modifier = 0.0


class StatsComponent:
    def __init__(self, config):
        """
        完善版属性组件：
        1. 自动过滤非数值配置。
        2. 确保核心战斗属性始终存在。
        3. 解决 damage_mult 基础倍率问题。
        """
        # --- 1. 工业级默认值规则 ---
        # 确保哪怕 JSON 是空的，游戏逻辑引用 self.stats.xxx 也不会崩溃
        self._defaults = {
            'health': 100.0,
            'max_health': 100.0,
            'move_speed': 350.0,
            'damage_mult': 1.0,  # 默认 1.0 倍伤害，解决“光环无伤害”
            'attack_area': 1.0,
            'cooldown_reduction': 0.0,
            'pickup_range': 150.0,
            'exp_gain': 1.0,
            'luck': 1.0,
            'armor': 0.0
        }

        # 合并配置 (JSON 中的值会覆盖默认值)
        merged_config = {**self._defaults, **config}

        # --- 2. 自动化属性映射 ---
        for key, val in merged_config.items():
            if isinstance(val, (int, float)):
                # 规则：如果是数值，包装成 Stat 对象
                # 特殊处理：health 初始化时通常等于 max_health
                if key == 'health' and 'max_health' in merged_config:
                    setattr(self, key, Stat(merged_config['max_health']))
                else:
                    setattr(self, key, Stat(val))
            else:
                # 规则：如果是字符串或其它，作为普通静态属性
                setattr(self, key, val)

    def add_modifier(self, stat_name, val, is_percent=True):
        """
        安全加成接口：
        一劳永逸点：即便尝试加成一个不存在的属性，也不会报错。
        """
        stat = getattr(self, stat_name, None)
        if isinstance(stat, Stat):
            if is_percent:
                stat.percent_modifier += val
            else:
                stat.flat_modifier += val
        else:
            # 动态防御：如果加成的是不存在的数值属性，则忽略
            pass

    def get_dict(self):
        """一键导出所有属性的最终值 (用于 UI 显示或存档)"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Stat):
                result[key] = value.value
            elif not key.startswith("_"):
                result[key] = value
        return result

    def health_check(self, current_hp):
        """
        辅助规则：确保当前血量不会超过实时计算的 max_health。
        用于升级增加最大生命值后，同步调整当前生命值。
        """
        max_h = self.max_health.value
        return min(current_hp, max_h)