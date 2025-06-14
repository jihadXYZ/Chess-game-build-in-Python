import pygame
import sys
import random
from enum import Enum
from copy import deepcopy
import time
import math

pygame.init()

chess_board_size = 8
square_pixel_size = 80
game_window_size = chess_board_size * square_pixel_size + 20  
right_sidebar_width = 220  
total_window_width = game_window_size + right_sidebar_width
piece_images = {}

pure_white = (255, 255, 255)
pure_black = (0, 0, 0)
dark_wood_square = (181, 136, 99)
light_wood_square = (240, 217, 181)
golden_selection_highlight = (255, 255, 0, 120)
green_move_highlight = (50, 205, 50, 100)
red_check_highlight = (220, 20, 60, 150)
orange_last_move_highlight = (255, 165, 0, 100)
brown_sidebar_background = (139, 69, 19)
button_normal_color = (205, 133, 63)
button_hover_color = (222, 184, 135)
cream_text_color = (245, 245, 220)
dark_brown_border = (101, 67, 33)
bright_gold = (255, 215, 0)
metallic_silver = (192, 192, 192)

class ChessPieceColor(Enum):
    WHITE = 'w'
    BLACK = 'b'
    
    @property
    def opposite(self):
        return ChessPieceColor.BLACK if self == ChessPieceColor.WHITE else ChessPieceColor.WHITE

class ChessPieceType(Enum):
    KING = 'k'
    QUEEN = 'q'
    ROOK = 'r'
    BISHOP = 'b'
    KNIGHT = 'n'
    PAWN = 'p'

class GamePlayMode(Enum):
    PLAYER_VS_PLAYER = 0
    PLAYER_VS_AI = 1

class ComputerDifficultyLevel(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

class ClickableButton:
    def __init__(self, x_position, y_position, button_width, button_height, display_text, click_action=None):
        self.rectangle = pygame.Rect(x_position, y_position, button_width, button_height)
        self.display_text = display_text
        self.click_action = click_action
        self.mouse_hovering = False
        
    def draw(self, game_screen):
        if self.mouse_hovering:
            light_color = tuple(min(255, color_value + 30) for color_value in button_hover_color)
            dark_color = button_hover_color
        else:
            light_color = tuple(min(255, color_value + 20) for color_value in button_normal_color)
            dark_color = button_normal_color
        
        for pixel_row in range(self.rectangle.height):
            blend_ratio = pixel_row / self.rectangle.height
            current_color = tuple(int(light_color[index] * (1 - blend_ratio) + dark_color[index] * blend_ratio) for index in range(3))
            pygame.draw.line(game_screen, current_color, 
                           (self.rectangle.left, self.rectangle.top + pixel_row), 
                           (self.rectangle.right, self.rectangle.top + pixel_row))
        
        border_highlight = bright_gold if self.mouse_hovering else dark_brown_border
        pygame.draw.rect(game_screen, border_highlight, self.rectangle, 2)
        
        inner_highlight_rect = pygame.Rect(self.rectangle.left + 1, self.rectangle.top + 1, 
                                self.rectangle.width - 2, self.rectangle.height - 2)
        bright_highlight_color = tuple(min(255, color_value + 40) for color_value in light_color)
        pygame.draw.line(game_screen, bright_highlight_color, inner_highlight_rect.topleft, inner_highlight_rect.topright)
        pygame.draw.line(game_screen, bright_highlight_color, inner_highlight_rect.topleft, inner_highlight_rect.bottomleft)
        
        button_font = pygame.font.SysFont('Times New Roman', 14, bold=True)
        
        text_shadow = button_font.render(self.display_text, True, (0, 0, 0, 100))
        shadow_position = text_shadow.get_rect(center=(self.rectangle.centerx + 1, self.rectangle.centery + 1))
        game_screen.blit(text_shadow, shadow_position)
        
        text_highlight_color = bright_gold if self.mouse_hovering else cream_text_color
        main_text_surface = button_font.render(self.display_text, True, text_highlight_color)
        text_center_position = main_text_surface.get_rect(center=self.rectangle.center)
        game_screen.blit(main_text_surface, text_center_position)
        
    def check_hover(self, mouse_position):
        self.mouse_hovering = self.rectangle.collidepoint(mouse_position)
        
    def handle_event(self, user_event):
        if user_event.type == pygame.MOUSEBUTTONDOWN and user_event.button == 1:
            if self.mouse_hovering and self.click_action:
                self.click_action()
                return True
        return False

def start_main_game():
    game_screen = pygame.display.set_mode((total_window_width, game_window_size))
    pygame.display.set_caption("Made by jihad")
    
    chess_game = ChessGameEngine(mode=GamePlayMode.PLAYER_VS_PLAYER)
    
    mouse_position = (0, 0)
    
    game_clock = pygame.time.Clock()
    game_running = True
    while game_running:
        for user_event in pygame.event.get():
            if user_event.type == pygame.QUIT:
                game_running = False
            elif user_event.type == pygame.MOUSEBUTTONDOWN:
                if user_event.button == 1:
                    chess_game.handle_click(user_event.pos)
            elif user_event.type == pygame.MOUSEMOTION:
                mouse_position = user_event.pos
                for button in chess_game.ui_buttons:
                    button.check_hover(mouse_position)
        
        if chess_game.game_mode == GamePlayMode.PLAYER_VS_AI and chess_game.current_turn == ChessPieceColor.BLACK and not chess_game.game_ended and chess_game.computer_thinking:
            chess_game.make_computer_move()
        
        if chess_game.game_mode == GamePlayMode.PLAYER_VS_AI and chess_game.current_turn == ChessPieceColor.BLACK and not chess_game.game_ended and not chess_game.computer_thinking:
            chess_game.computer_thinking = True
        
        game_screen.fill(pure_white)
        chess_game.draw(game_screen)
        pygame.display.flip()
        
        game_clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    start_main_game()
