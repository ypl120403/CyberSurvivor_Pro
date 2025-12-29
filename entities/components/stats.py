class Stat:
    """属性容器：只处理数值"""

    def __init__(self, base_value):
        # 强制转换，确保计算安全
        try:
            self.base_value = float(base_value)
        except (ValueError, TypeError):
            self.base_value = 0.0

        self.flat_modifier = 0.0
        self.percent_modifier = 0.0

    @property
    def value(self):
        return (self.base_value + self.flat_modifier) * (1 + self.percent_modifier)


class StatsComponent:
    def __init__(self, config):
        """
        智能化属性组件：
        1. 自动识别数字类型的配置并转化为 Stat。
        2. 自动忽略 ID、Name、Desc 等文本信息。
        """
        # 默认核心属性
        defaults = {
            'health': 100,
            'max_health': 100,
            'move_speed': 350,
            'damage_mult': 1.0,
            'attack_area': 1.0,
            'cooldown_reduction': 0.0,
            'pickup_range': 120,
            'exp_gain': 1.0,
            'luck': 1.0,
            'armor': 0
        }

        # 合并默认值与传入配置
        merged_config = {**defaults, **config}

        # 遍历所有配置项
        for key, val in merged_config.items():
            # 核心规则：只有当值是 [整数] 或 [浮点数] 时，才创建 Stat 对象
            if isinstance(val, (int, float)):
                # 特殊逻辑：如果是初始化 health，自动对齐到 max_health
                if key == 'health' and 'max_health' in merged_config:
                    setattr(self, key, Stat(merged_config['max_health']))
                else:
                    setattr(self, key, Stat(val))
            else:
                # 规则：如果是字符串(如 id, name)，直接作为普通属性保存，不包装成 Stat
                setattr(self, key, val)

    def add_modifier(self, stat_name, val, is_percent=True):
        """安全加成方法"""
        stat = getattr(self, stat_name, None)
        # 只有 Stat 类型的对象才能添加加成
        if isinstance(stat, Stat):
            if is_percent:
                stat.percent_modifier += val
            else:
                stat.flat_modifier += val
        else:
            # 静默跳过非数值属性的加成请求
            pass

    def get_all_stats(self):
        """导出所有数值属性的最终值"""
        return {k: v.value for k, v in self.__dict__.items() if isinstance(v, Stat)}