# ui/components.py
import pygame


class CyberButton:
    """赛博风格发光按钮"""

    def __init__(self, text, pos, size, font, color=(0, 255, 240)):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.font = font
        self.base_color = pygame.Color(*color)
        self.is_hovered = False
        self.glow_anim = 0.0  # 动画进度

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        # 呼吸灯逻辑：悬停时发光增强
        if self.is_hovered:
            self.glow_anim = min(1.0, self.glow_anim + 0.1)
        else:
            self.glow_anim = max(0.0, self.glow_anim - 0.05)

    def draw(self, surface):
        # 1. 绘制外发光底色
        if self.glow_anim > 0:
            # 这里的 inflate 稍微扩大一点矩形作为发光范围
            glow_rect = self.rect.inflate(int(self.glow_anim * 12), int(self.glow_anim * 12))
            glow_color = (*self.base_color[:3], int(self.glow_anim * 50))
            glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=8)
            surface.blit(glow_surf, glow_rect.topleft)

        # 2. 绘制主边框
        current_color = self.base_color if self.is_hovered else self.base_color.lerp((0, 0, 0, 255), 0.5)
        pygame.draw.rect(surface, current_color, self.rect, 2, border_radius=4)

        # 3. 核心修复：绘制四个装饰角 (使用 Vector2 避免元组拼接错误)
        l = 10  # 角线长度
        tl = pygame.Vector2(self.rect.topleft)
        tr = pygame.Vector2(self.rect.topright)
        bl = pygame.Vector2(self.rect.bottomleft)
        br = pygame.Vector2(self.rect.bottomright)

        # 左上角
        pygame.draw.lines(surface, self.base_color, False, [tl + (0, l), tl, tl + (l, 0)], 3)
        # 右下角
        pygame.draw.lines(surface, self.base_color, False, [br - (0, l), br, br - (l, 0)], 3)

        # 4. 文字绘制
        t_surf = self.font.render(self.text, True, current_color)
        t_rect = t_surf.get_rect(center=self.rect.center)
        surface.blit(t_surf, t_rect)