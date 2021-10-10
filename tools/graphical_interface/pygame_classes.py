import pygame

class pygame_screen:
    def __init__(self, res, bck_color=None, path_img=None, caption=""):
        self.resolution = res
        self.screen = pygame.display.set_mode(res)
        self.color = bck_color
        self.bck_original = pygame.image.load(path_img).convert_alpha()
        self.bck = self.bck_original
        pygame.display.set_caption(caption)

    def draw(self):
        self.screen.fill(self.color)
        if (self.bck):
            bck_res = (self.bck.get_width(), self.bck.get_height())
            res = (self.screen.get_width(), self.screen.get_height())
            if (res[0] < res[1]):
                self.bck = pygame.transform.scale(self.bck_original, (res[0], int(bck_res[1] * res[0] / bck_res[0])))
            else:
                self.bck = pygame.transform.scale(self.bck_original, (int(bck_res[0] * res[1] / bck_res[1]), res[1]))
            self.screen.blit(self.bck, (0, 0))

    def get_screen_size(self):
        return self.resolution
    
    def get_screen(self):
        return self.screen

class pygame_img:
    def __init__(self, pos, size, path_img, alpha=255, text="", text_color=(255,255,255), font="Segoe Print", font_size=15):
        self.size = size
        self.position = pos
        self.surface = pygame.Surface(size)
        self.img_original = pygame.image.load(path_img).convert_alpha()
        self.img = self.img_original
        self.img.set_alpha(alpha)
        self.rect = self.surface.get_rect(center=pos)
        self.font = pygame.font.SysFont(font, font_size)
        self.text = text
        self.text_color = text_color
        self.text_surf = self.font.render(self.text, 1, text_color)
        self.text_pos = self.text_surf.get_rect(center=pos)

    def set_size(self, size):
        self.size = size
        self.surface = pygame.Surface(size)
        self.rect = self.surface.get_rect(center=self.position)

    def set_position(self, pos):
        self.position = pos
        self.rect = self.surface.get_rect(center=pos)
        self.text_pos = self.text_surf.get_rect(center=pos)

    def set_img(self, path_img):
        self.img_original = pygame.image.load(path_img).convert_alpha()
        self.img = self.img_original

    def set_text(self, text):
        self.text = text
        self.text_surf = self.font.render(self.text, 1, self.text_color)

    def draw(self, screen):
        self.img = pygame.transform.scale(self.img_original, (self.size[0], self.size[1]))
        self.surface = self.img
        screen.blit(self.surface, self.rect)
        screen.blit(self.text_surf, self.text_pos)

class pygame_button:
    def __init__(self, pos, size, action=None, text="", color=(100,100,100), hover_color=(150,150,150), text_color=(255,255,255), font="Segoe Print", font_size=15):
        self.size = size
        self.position = pos
        self.surface = pygame.Surface(size)
        self.rect = self.surface.get_rect(center=pos)
        self.font = pygame.font.SysFont(font, font_size)
        self.text = text
        self.text_surf = self.font.render(self.text, 1, text_color)
        self.text_pos = self.text_surf.get_rect(center=pos)
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.actual_color = color

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_over(mouse_pos)
        self.surface.fill(self.actual_color)
        screen.blit(self.surface, self.rect)
        screen.blit(self.text_surf, self.text_pos)

    def mouse_over(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.actual_color = self.hover_color
            return True
        self.actual_color = self.color
        return False

    def call_back(self, *args):
        if self.action:
            return self.action(*args)

class pygame_text:
    def __init__(self, text, position, color=[100, 100, 100], font="Segoe Print", font_size=15, centered=False):
        self.position = position
        self.color = color
        self.font = pygame.font.SysFont(font, font_size)
        self.text_surf = self.font.render(text, 1, color)

        if len(color) == 4:
            self.text_surf.set_alpha(color[3])
        if centered:
            self.position = self.text_surf.get_rect(center=position)

    def text(self, text):
        self.text_surf = self.font.render(text, 1, self.color)

    def draw(self, screen):
        screen.blit(self.text_surf, self.position)
