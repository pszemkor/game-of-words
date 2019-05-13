# GLOBAL PARAMETERS
# view parameters - width 1000 px.  , height 700 px.

import pygame
import controller

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
BOARD_SIZE = 15

FIELD_RECTANGLE = (28, 28)


class FieldSprite(pygame.sprite.Sprite):
    def __init__(self, field, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.image = pygame.Surface(FIELD_RECTANGLE)
        self.image.fill((0, 255, 255))

        self.field = field


class GameView:
    # def __init__(self, evManager):
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.register(self)

        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Word of Games')
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((0, 0, 0))
        font = pygame.font.Font(None, 150)
        text = "Game of Words"
        text_img = font.render(text, 1, (255, 255, 255))
        text_rec = text_img.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT/ 2))
        self.background.blit(text_img, text_rec)
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()

        self.back_sprites = pygame.sprite.RenderUpdates()
        self.front_sprites = pygame.sprite.RenderUpdates()
        self.board_sprites = pygame.sprite.RenderUpdates()

        pygame.time.delay(2000)

    def show_board(self, board):
        self.background.fill((0, 0, 0))
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()

        field_rect = pygame.Rect((100, 0, FIELD_RECTANGLE[0], FIELD_RECTANGLE[0]))

        column = 0
        field_rectangle_width = FIELD_RECTANGLE[0] + 2
        for row in board.fields:
            for field in row:
                if column < BOARD_SIZE:
                    field_rect = field_rect.move(field_rectangle_width, 0)
                else:
                    column = 0
                    field_rect = field_rect.move(-(BOARD_SIZE - 1) * field_rectangle_width, field_rectangle_width)
                column += 1
                new_field_sprite = FieldSprite(field, self.back_sprites)
                new_field_sprite.rect = field_rect
                new_field_sprite = None

        # while True:
        #     self.draw_everything()

    def draw_everything(self):
        self.back_sprites.clear(self.window, self.background)
        self.front_sprites.clear(self.window, self.background)
        self.board_sprites.clear(self.window, self.background)


        self.back_sprites.update()
        self.front_sprites.update()

        dirty_rects1 = self.back_sprites.draw(self.window)
        dirty_rects2 = self.front_sprites.draw(self.window)

        dirty_rects = dirty_rects1 + dirty_rects2
        pygame.display.update(dirty_rects)

    def notify(self, event):
        if isinstance(event, controller.TickEvent):
            self.draw_everything()
        elif isinstance(event, controller.BoardBuildEvent):
            self.show_board(event.board)
