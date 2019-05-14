# GLOBAL PARAMETERS
# view parameters - width 1000 px., height 700 px.

import pygame
from enum import Enum

import config
import controller
import model


class FieldSprite(pygame.sprite.Sprite):
    def __init__(self, field, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.field = field
        self.image = pygame.Surface(config.FIELD_RECTANGLE)
        self.update()

    def update(self):

        if self.field.is_active:
            self.image.fill((255, 255, 0))
        else:
            self.image.fill((0, 255, 255))

        if self.field.state is model.FieldState.FIXED:
            self.image.fill((200, 50, 0))
            font = pygame.font.Font(None, config.FIELD_RECTANGLE[0])
            text = self.field.tile.__str__()
            text_img = font.render(text, 1, (255, 255, 255))
            text_rec = text_img.get_rect(center=(config.FIELD_RECTANGLE[0] // 2, config.FIELD_RECTANGLE[0] // 2))
            self.image.blit(text_img, text_rec)
        elif self.field.state is model.FieldState.TEMPORARY:
            font = pygame.font.Font(None, config.FIELD_RECTANGLE[0])
            text = self.field.tile.__str__()
            text_img = font.render(text, 1, (255, 255, 255))
            text_rec = text_img.get_rect(center=(config.FIELD_RECTANGLE[0] // 2, config.FIELD_RECTANGLE[0] // 2))
            self.image.blit(text_img, text_rec)


class ButtonSprite(pygame.sprite.Sprite):
    def __init__(self, button, group=None):
        pygame.sprite.Sprite.__init__(self, group)
        self.button = button
        self.image = pygame.Surface(self.button.shape)
        self.update()

    def update(self):
        if self.button.type is ButtonShapeType.RECTANGLE:
            self.image.fill(self.button.bg_color)
            font = pygame.font.Font(None, self.button.font_size)
            text_img = font.render(self.button.text, 1, (255, 255, 255))
            text_rec = text_img.get_rect(center=(self.button.shape[0] // 2, self.button.shape[1] // 2))
            self.image.blit(text_img, text_rec)
        elif self.button.type is ButtonShapeType.CIRCLE:
            pygame.draw.circle(self.image, self.button.bg_color, self.button.shape[0] // 2, self.button.shape[0] // 2)
            font = pygame.font.Font(None, self.button.font_size)
            text_img = font.render(self.button.text, 1, (255, 255, 255))
            text_rec = text_img.get_rect(center=(self.button.shape[0] // 2, self.button.shape[0] // 2))
            self.image.blit(text_img, text_rec)


class ButtonShapeType(Enum):
    RECTANGLE = 0
    CIRCLE = 1


class Button:
    def __init__(self, type, text, font_size, bg_color, shape, left_edge_offset, top_edge_offset):
        self.type = type
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.shape = shape
        self.left_edge_offset = left_edge_offset
        self.top_edge_offset = top_edge_offset


class GameView:
    # def __init__(self, evManager):
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.register(self)

        pygame.init()
        self.window = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption('Word of Games')
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((0, 0, 0))
        font = pygame.font.Font(None, 150)
        text = "Game of Words"
        text_img = font.render(text, 1, (255, 255, 255))
        text_rec = text_img.get_rect(center=(config.WINDOW_WIDTH / 2, config.WINDOW_HEIGHT / 2))
        self.background.blit(text_img, text_rec)
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()

        self.back_sprites = pygame.sprite.RenderUpdates()
        self.front_sprites = pygame.sprite.RenderUpdates()

        # pygame.time.delay(2000)
        pygame.time.delay(200)

    def show_board(self, board):
        self.background.fill((0, 0, 0))
        self.window.blit(self.background, (0, 0))
        pygame.display.flip()

        field_rect = pygame.Rect(
            (config.LEFT_EDGE_BOARD_OFFSET - config.FIELD_RECTANGLE_WIDTH, config.TOP_EDGE_BOARD_OFFSET,
             config.FIELD_RECTANGLE[0], config.FIELD_RECTANGLE[0]))

        column = 0

        field_rect = pygame.Rect(
            (config.LEFT_EDGE_BOARD_OFFSET - config.FIELD_RECTANGLE_WIDTH, config.TOP_EDGE_BOARD_OFFSET,
             config.FIELD_RECTANGLE[0], config.FIELD_RECTANGLE[0]))

        for row in board.fields:
            for field in row:
                if column < config.BOARD_SIZE:
                    field_rect = field_rect.move(config.FIELD_RECTANGLE_WIDTH, 0)
                else:
                    column = 0
                    field_rect = field_rect.move(-(config.BOARD_SIZE - 1) * config.FIELD_RECTANGLE_WIDTH,
                                                 config.FIELD_RECTANGLE_WIDTH)
                column += 1
                new_field_sprite = FieldSprite(field, self.back_sprites)
                new_field_sprite.rect = field_rect
                new_field_sprite = None



    def show_tilebox(self, tilebox):
        field_rect = pygame.Rect(
            (config.LEFT_EDGE_TILEBOX_OFFSET - config.FIELD_RECTANGLE_WIDTH, config.TOP_EDGE_TILEBOX_OFFSET,
             config.FIELD_RECTANGLE[0],
             config.FIELD_RECTANGLE[0]))

        column = 0
        for field in tilebox.fields:
            field_rect = field_rect.move(config.FIELD_RECTANGLE_WIDTH, 0)
            new_field_sprite = FieldSprite(field, self.back_sprites)
            new_field_sprite.rect = field_rect
            new_field_sprite = None

    # buttons are drawn in the foreground
    def show_button(self, button):
        button_rect = pygame.Rect((button.left_edge_offset, button.top_edge_offset,
                                   button.shape[0], button.shape[1] if button.type == ButtonShapeType.RECTANGLE
                                   else button.shape[0]))
        new_button_sprite = ButtonSprite(button, self.front_sprites)
        new_button_sprite.rect = button_rect

        pass

    def show_buttons(self, buttons):
        for button in buttons:
            self.show_button(button)

    def draw_everything(self):
        self.back_sprites.clear(self.window, self.background)
        self.front_sprites.clear(self.window, self.background)

        self.back_sprites.update()
        self.front_sprites.update()

        dirty_rects1 = self.back_sprites.draw(self.window)
        dirty_rects2 = self.front_sprites.draw(self.window)

        dirty_rects = dirty_rects1 + dirty_rects2
        pygame.display.update(dirty_rects)

    def get_field_sprite(self, field):
        for sprite in self.back_sprites:
            if hasattr(sprite, "field") and sprite.field == field:
                return sprite

    def notify(self, event):
        if isinstance(event, controller.TickEvent):
            self.draw_everything()
        elif isinstance(event, controller.BoardBuildEvent):
            self.show_board(event.board)
        elif isinstance(event, controller.TileBoxBuildEvent):
            self.show_tilebox(event.tilebox)
        elif isinstance(event, controller.UpdateFieldEvent):
            self.get_field_sprite(event.field)
        elif isinstance(event, controller.DrawGameButtonsEvent):
            self.show_buttons(event.buttons)
