import pygame

class BaseScene:
    """所有场景的基类：菜单、战斗、结算都继承自它"""
    def __init__(self, engine):
        self.engine = engine
        self.screen = pygame.display.get_surface()

    def update(self, dt):
        pass

    def draw(self):
        pass