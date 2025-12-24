import pygame


class CombatUtils:
    @staticmethod
    def get_nearest_enemy(origin_pos, enemy_group):
        """在指定的敌人组中寻找距离原点最近的敌人"""
        nearest_enemy = None
        min_dist = float('inf')

        for enemy in enemy_group:
            # 计算向量距离
            dist = origin_pos.distance_to(enemy.pos)
            if dist < min_dist:
                min_dist = dist
                nearest_enemy = enemy

        return nearest_enemy