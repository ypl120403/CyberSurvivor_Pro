import pygame
import random
from src.core.event_bus import bus


class DamageSystem:
    @staticmethod
    def apply_damage(engine, victim, base_amount, attacker_config=None, player=None):
        """
        [维度 4, 5, 6, 10, 11, 12] 综合伤害解释器
        base_amount: 基础伤害数值
        attacker_config: 发起攻击的武器/子弹 JSON 配置
        """
        if not victim or not victim.alive(): return False

        # --- 1. 上下文与环境协同计算 (维度 10 & 11) ---
        final_damage = base_amount

        if attacker_config:
            # [维度 11] 环境协同: 如果目标有特定状态，伤害加倍
            synergy = attacker_config.get("synergy", {})
            if synergy:
                target_debuffs = getattr(victim, 'debuffs', [])
                if synergy.get("if_target_has_debuff") in target_debuffs:
                    final_damage *= synergy.get("multiplier", 1.5)

            # [维度 10] 上下文条件: 例如血量低于20%伤害加倍
            conditionals = attacker_config.get("conditionals", {})
            if player and conditionals:
                hp_percent = (player.current_hp / player.stats.max_health.value) * 100
                if hp_percent < conditionals.get("if_hp_below", 0):
                    final_damage *= conditionals.get("then_mult", 1.0)

        # --- 2. 物理扣血执行 ---
        is_dead = victim.take_damage(final_damage)

        # --- 3. 视觉打击感注入 (维度 12) ---
        if attacker_config:
            visuals = attacker_config.get("visuals", {})
            # 屏幕震动
            if "shake_intensity" in visuals:
                engine.scene.all_sprites.apply_shake(visuals["shake_intensity"])
            # 停顿时间 (Hit Stop) - 模拟打击感
            if "hit_stop_duration" in visuals:
                # 这种微小的停顿能极大地提升打击感
                pygame.time.delay(int(visuals["hit_stop_duration"]))

        # 弹出伤害数字
        engine.ui_manager.spawn_damage_text(victim.rect.center, final_damage)

        # --- 4. 事件钩子点火 (维度 6) ---
        if attacker_config and "events" in attacker_config:
            for hook in attacker_config["events"]:
                if hook["trigger"] == "on_hit":
                    if random.random() < hook.get("chance", 1.0):
                        DamageSystem._execute_proc(engine, hook, victim, player)

        # --- 5. 死亡判定与特权处理 (维度 5) ---
        if is_dead:
            # [维度 5] 特权标签：吸血 (Vampire)
            if player and "vampire" in getattr(player, 'privilege_tags', set()):
                # 杀敌回复 1% 血量
                heal_amount = player.stats.max_health.value * 0.01
                player.current_hp = min(player.stats.max_health.value, player.current_hp + heal_amount)

            # 触发全球击杀逻辑
            engine.on_enemy_killed(victim)

            # [维度 6] 杀敌钩子
            if attacker_config and "events" in attacker_config:
                for hook in attacker_config["events"]:
                    if hook["trigger"] == "on_kill":
                        DamageSystem._execute_proc(engine, hook, victim, player)

        return is_dead

    @staticmethod
    def handle_collision(bullet, enemy, engine):
        """
        专门处理子弹/回旋镖碰撞。
        增加安全检查：只有具备 damage 属性的对象才会被处理。
        """
        # 维度 0：安全检查，防止非子弹实体（如光环）误入碰撞逻辑
        if not hasattr(bullet, 'damage'):
            return False

        player = getattr(bullet, 'player', None)
        config = getattr(bullet, 'config', None)

        is_dead = DamageSystem.apply_damage(
            engine, enemy, bullet.damage,
            attacker_config=config,
            player=player
        )

        # 维度 3：执行子弹的命中反馈（销毁/穿透）
        if hasattr(bullet, 'on_hit'):
            bullet.on_hit()

        return is_dead

    @staticmethod
    def _execute_proc(engine, hook, victim, player):
        """
        维度 6: 概率触发动作的执行器
        """
        action = hook.get("action")

        # 动作 A: 在目标位置生成区域效果 (如 EMP、爆炸)
        if action == "spawn_area":
            from src.entities.area_effect import AreaEffectEntity
            from src.core.registry import registry
            sub_id = hook.get("id")
            sub_config = registry.weapons.get(sub_id)
            if sub_config:
                AreaEffectEntity(victim.rect.center, [engine.scene.all_sprites], player, sub_config)

        # 动作 B: 施加减速/眩晕等 Debuff
        elif action == "apply_debuff":
            debuff_id = hook.get("id")
            if hasattr(victim, 'apply_debuff'):
                victim.apply_debuff(debuff_id)