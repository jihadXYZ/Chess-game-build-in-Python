"""
Made by jihad - Chess Game
"""

import pygame
import sys
import random
from enum import Enum
from copy import deepcopy
import time
import math

pygame.init()

BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE + 20  
SIDEBAR_WIDTH = 220  
WINDOW_WIDTH = WINDOW_SIZE + SIDEBAR_WIDTH
IMAGES = {}

pure_white = (255, 255, 255)
pure_black = (0, 0, 0)
DARK_SQUARE = (181, 136, 99)
LIGHT_SQUARE = (240, 217, 181)
HIGHLIGHT = (255, 255, 0, 120)
MOVE_HIGHLIGHT = (50, 205, 50, 100)
CHECK_HIGHLIGHT = (220, 20, 60, 150)
LAST_MOVE_HIGHLIGHT = (255, 165, 0, 100)
SIDEBAR_BG = (139, 69, 19)
BUTTON_COLOR = (205, 133, 63)
BUTTON_HOVER = (222, 184, 135)
TEXT_COLOR = (245, 245, 220)
BORDER_COLOR = (101, 67, 33)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# Piece colors
class Color(Enum):
    WHITE = 'w'
    BLACK = 'b'
    
    @property
    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

class PieceType(Enum):
    KING = 'k'
    QUEEN = 'q'
    ROOK = 'r'
    BISHOP = 'b'
    KNIGHT = 'n'
    PAWN = 'p'

class GameMode(Enum):
    PLAYER_VS_PLAYER = 0
    PLAYER_VS_AI = 1

class AIDifficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

class Button:
    def __init__(self, x_position, y_position, button_width, button_height, display_text, click_action=None):
        self.rect = pygame.Rect(x_position, y_position, button_width, button_height)
        self.text = display_text
        self.action = click_action
        self.hovered = False
        
    def draw(self, game_screen):
        if self.hovered:
            light_color = tuple(min(255, color_value + 30) for color_value in BUTTON_HOVER)
            dark_color = BUTTON_HOVER
        else:
            light_color = tuple(min(255, color_value + 20) for color_value in BUTTON_COLOR)
            dark_color = BUTTON_COLOR
        
        for pixel_row in range(self.rect.height):
            blend_ratio = pixel_row / self.rect.height
            current_color = tuple(int(light_color[index] * (1 - blend_ratio) + dark_color[index] * blend_ratio) for index in range(3))
            pygame.draw.line(game_screen, current_color, 
                           (self.rect.left, self.rect.top + pixel_row), 
                           (self.rect.right, self.rect.top + pixel_row))
        
        border_highlight = GOLD if self.hovered else BORDER_COLOR
        pygame.draw.rect(game_screen, border_highlight, self.rect, 2)
        
        inner_highlight_rect = pygame.Rect(self.rect.left + 1, self.rect.top + 1, 
                                self.rect.width - 2, self.rect.height - 2)
        bright_highlight_color = tuple(min(255, color_value + 40) for color_value in light_color)
        pygame.draw.line(game_screen, bright_highlight_color, inner_highlight_rect.topleft, inner_highlight_rect.topright)
        pygame.draw.line(game_screen, bright_highlight_color, inner_highlight_rect.topleft, inner_highlight_rect.bottomleft)
        
        button_font = pygame.font.SysFont('Times New Roman', 14, bold=True)
        
        text_shadow = button_font.render(self.text, True, (0, 0, 0, 100))
        shadow_position = text_shadow.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        game_screen.blit(text_shadow, shadow_position)
        
        text_highlight_color = GOLD if self.hovered else TEXT_COLOR
        main_text_surface = button_font.render(self.text, True, text_highlight_color)
        text_center_position = main_text_surface.get_rect(center=self.rect.center)
        game_screen.blit(main_text_surface, text_center_position)
        
    def check_hover(self, mouse_position):
        self.hovered = self.rect.collidepoint(mouse_position)
        
    def handle_event(self, user_event):
        if user_event.type == pygame.MOUSEBUTTONDOWN and user_event.button == 1:
            if self.hovered and self.action:
                self.action()
                return True
        return False

class Piece:
    def __init__(self, chess_piece_type, piece_color, board_position):
        self.type = chess_piece_type
        self.color = piece_color
        self.position = board_position
        self.has_moved = False
        self.image_key = f"{piece_color.value}{chess_piece_type.value}"
    
    def get_possible_moves(self, chess_board, previous_move=None, validate_check=True):
        current_row, current_col = self.position
        available_moves = []
        
        if self.type == PieceType.PAWN:
            move_direction = -1 if self.color == Color.WHITE else 1
            
            if 0 <= current_row + move_direction < BOARD_SIZE and chess_board[current_row + move_direction][current_col] is None:
                available_moves.append((current_row + move_direction, current_col))
                
                if ((self.color == Color.WHITE and current_row == 6) or 
                    (self.color == Color.BLACK and current_row == 1)) and \
                   0 <= current_row + 2*move_direction < BOARD_SIZE and \
                   chess_board[current_row + 2*move_direction][current_col] is None:
                    available_moves.append((current_row + 2*move_direction, current_col))
            
            for column_offset in [-1, 1]:
                if 0 <= current_row + move_direction < BOARD_SIZE and 0 <= current_col + column_offset < BOARD_SIZE:
                    target_piece = chess_board[current_row + move_direction][current_col + column_offset]
                    if target_piece and target_piece.color != self.color:
                        available_moves.append((current_row + move_direction, current_col + column_offset))
            
            if previous_move and previous_move['piece'].type == PieceType.PAWN:
                last_from_row, last_from_col = previous_move['from']
                last_to_row, last_to_col = previous_move['to']
                
                if abs(last_from_row - last_to_row) == 2:
                    if current_row == last_to_row and abs(current_col - last_to_col) == 1:
                        available_moves.append((current_row + move_direction, last_to_col))
        
        elif self.type == PieceType.KNIGHT:
            knight_moves = [
                (current_row-2, current_col-1), (current_row-2, current_col+1),
                (current_row-1, current_col-2), (current_row-1, current_col+2),
                (current_row+1, current_col-2), (current_row+1, current_col+2),
                (current_row+2, current_col-1), (current_row+2, current_col+1)
            ]
            
            for move in knight_moves:
                r, c = move
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if chess_board[r][c] is None or chess_board[r][c].color != self.color:
                        available_moves.append(move)
        
        elif self.type == PieceType.BISHOP:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    r, c = current_row + i*dr, current_col + i*dc
                    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                        break
                    if chess_board[r][c] is None:
                        available_moves.append((r, c))
                    elif chess_board[r][c].color != self.color:
                        available_moves.append((r, c))
                        break
                    else:
                        break
        
        elif self.type == PieceType.ROOK:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    r, c = current_row + i*dr, current_col + i*dc
                    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                        break
                    if chess_board[r][c] is None:
                        available_moves.append((r, c))
                    elif chess_board[r][c].color != self.color:
                        available_moves.append((r, c))
                        break
                    else:
                        break
        
        elif self.type == PieceType.QUEEN:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                for i in range(1, BOARD_SIZE):
                    r, c = current_row + i*dr, current_col + i*dc
                    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                        break
                    if chess_board[r][c] is None:
                        available_moves.append((r, c))
                    elif chess_board[r][c].color != self.color:
                        available_moves.append((r, c))
                        break
                    else:
                        break
        
        elif self.type == PieceType.KING:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                r, c = current_row + dr, current_col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if chess_board[r][c] is None or chess_board[r][c].color != self.color:
                        available_moves.append((r, c))
            
            if not self.has_moved and not self.is_in_check(chess_board):
                if current_col + 3 < BOARD_SIZE and chess_board[current_row][current_col+3] is not None and \
                   chess_board[current_row][current_col+3].type == PieceType.ROOK and \
                   not chess_board[current_row][current_col+3].has_moved and \
                   chess_board[current_row][current_col+1] is None and chess_board[current_row][current_col+2] is None:
                    if not self.would_be_in_check(chess_board, (current_row, current_col+1)) and \
                       not self.would_be_in_check(chess_board, (current_row, current_col+2)):
                        available_moves.append((current_row, current_col+2))
                
                if current_col - 4 >= 0 and chess_board[current_row][current_col-4] is not None and \
                   chess_board[current_row][current_col-4].type == PieceType.ROOK and \
                   not chess_board[current_row][current_col-4].has_moved and \
                   chess_board[current_row][current_col-1] is None and chess_board[current_row][current_col-2] is None and \
                   chess_board[current_row][current_col-3] is None:
                    if not self.would_be_in_check(chess_board, (current_row, current_col-1)) and \
                       not self.would_be_in_check(chess_board, (current_row, current_col-2)):
                        available_moves.append((current_row, current_col-2))
        
        if validate_check:
            legal_moves = []
            for move in available_moves:
                if not self.move_would_cause_check(chess_board, move):
                    legal_moves.append(move)
            return legal_moves
        
        return available_moves
    
    def move_would_cause_check(self, board, move):
        # Create a copy of the board
        board_copy = [row[:] for row in board]
        
        # Get the king
        king = None
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board_copy[r][c] and board_copy[r][c].type == PieceType.KING and \
                   board_copy[r][c].color == self.color:
                    king = board_copy[r][c]
                    break
            if king:
                break
        
        # Make the move on the copy
        old_row, old_col = self.position
        new_row, new_col = move
        
        # Handle en passant capture
        captured_piece = board_copy[new_row][new_col]
        if self.type == PieceType.PAWN and old_col != new_col and not captured_piece:
            # This is an en passant capture
            captured_piece = board_copy[old_row][new_col]
            board_copy[old_row][new_col] = None
        
        # Move the piece
        board_copy[new_row][new_col] = self
        board_copy[old_row][old_col] = None
        
        # Update king position if we're moving the king
        if self.type == PieceType.KING:
            king.position = move
        
        # Check if the king is in check after the move
        return king.is_in_check(board_copy)
    
    def is_in_check(self, board):
        # Only kings can be in check
        if self.type != PieceType.KING:
            return False
        
        row, col = self.position
        
        # Check for attacks from each direction
        
        # Knight attacks
        knight_moves = [
            (row-2, col-1), (row-2, col+1),
            (row-1, col-2), (row-1, col+2),
            (row+1, col-2), (row+1, col+2),
            (row+2, col-1), (row+2, col+1)
        ]
        
        for r, c in knight_moves:
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                piece = board[r][c]
                if piece and piece.color != self.color and piece.type == PieceType.KNIGHT:
                    return True
        
        # Pawn attacks
        pawn_direction = 1 if self.color == Color.WHITE else -1
        for c_offset in [-1, 1]:
            r, c = row + pawn_direction, col + c_offset
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                piece = board[r][c]
                if piece and piece.color != self.color and piece.type == PieceType.PAWN:
                    return True
        
        # Rook/Queen attacks (horizontal and vertical)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                piece = board[r][c]
                if piece:
                    if piece.color != self.color and (piece.type == PieceType.ROOK or piece.type == PieceType.QUEEN):
                        return True
                    break
        
        # Bishop/Queen attacks (diagonal)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                piece = board[r][c]
                if piece:
                    if piece.color != self.color and (piece.type == PieceType.BISHOP or piece.type == PieceType.QUEEN):
                        return True
                    break
        
        # King attacks (for adjacent kings)
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                piece = board[r][c]
                if piece and piece.color != self.color and piece.type == PieceType.KING:
                    return True
        
        return False
    
    def would_be_in_check(self, board, position):
        # Create a copy of the board
        board_copy = [row[:] for row in board]
        
        # Move the king to the new position
        old_row, old_col = self.position
        new_row, new_col = position
        
        board_copy[new_row][new_col] = self
        board_copy[old_row][old_col] = None
        
        # Create a temporary king at the new position
        temp_king = Piece(PieceType.KING, self.color, position)
        
        # Check if the king would be in check
        return temp_king.is_in_check(board_copy)

class ChessAI:
    def __init__(self, difficulty=AIDifficulty.MEDIUM):
        self.difficulty = difficulty
        self.piece_values = {
            PieceType.PAWN: 10,
            PieceType.KNIGHT: 30,
            PieceType.BISHOP: 30,
            PieceType.ROOK: 50,
            PieceType.QUEEN: 90,
            PieceType.KING: 900
        }
        
        # Position evaluation tables to encourage good piece positioning
        self.position_values = {
            PieceType.PAWN: [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5, 5, 10, 25, 25, 10, 5, 5],
                [0, 0, 0, 20, 20, 0, 0, 0],
                [5, -5, -10, 0, 0, -10, -5, 5],
                [5, 10, 10, -20, -20, 10, 10, 5],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ],
            PieceType.KNIGHT: [
                [-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20, 0, 0, 0, 0, -20, -40],
                [-30, 0, 10, 15, 15, 10, 0, -30],
                [-30, 5, 15, 20, 20, 15, 5, -30],
                [-30, 0, 15, 20, 20, 15, 0, -30],
                [-30, 5, 10, 15, 15, 10, 5, -30],
                [-40, -20, 0, 5, 5, 0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]
            ],
            PieceType.BISHOP: [
                [-20, -10, -10, -10, -10, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 10, 10, 10, 10, 0, -10],
                [-10, 5, 5, 10, 10, 5, 5, -10],
                [-10, 0, 5, 10, 10, 5, 0, -10],
                [-10, 10, 10, 10, 10, 10, 10, -10],
                [-10, 5, 0, 0, 0, 0, 5, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20]
            ],
            PieceType.ROOK: [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [5, 10, 10, 10, 10, 10, 10, 5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [-5, 0, 0, 0, 0, 0, 0, -5],
                [0, 0, 0, 5, 5, 0, 0, 0]
            ],
            PieceType.QUEEN: [
                [-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]
            ],
            PieceType.KING: [
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-30, -40, -40, -50, -50, -40, -40, -30],
                [-20, -30, -30, -40, -40, -30, -30, -20],
                [-10, -20, -20, -20, -20, -20, -20, -10],
                [20, 20, 0, 0, 0, 0, 20, 20],
                [20, 30, 10, 0, 0, 10, 30, 20]
            ]
        }
    
    def get_move(self, game):
        # Make a deep copy of the game to avoid modifying the original
        game_copy = deepcopy(game)
        
        # Get the depth based on difficulty
        depth = self.difficulty.value
        
        # Get all possible moves for the AI
        all_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = game_copy.board[row][col]
                if piece and piece.color == game_copy.turn:
                    moves = piece.get_possible_moves(game_copy.board, game_copy.last_move)
                    for move in moves:
                        all_moves.append((piece, move))
        
        if not all_moves:
            return None
        
        # For easy difficulty, just make a random move
        if self.difficulty == AIDifficulty.EASY:
            return random.choice(all_moves)
        
        # For other difficulties, use minimax with alpha-beta pruning
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        for piece, move in all_moves:
            # Make the move
            old_row, old_col = piece.position
            new_row, new_col = move
            
            # Save the state
            captured_piece = game_copy.board[new_row][new_col]
            
            # Handle en passant capture
            if piece.type == PieceType.PAWN and old_col != new_col and not captured_piece:
                # This is an en passant capture
                captured_piece = game_copy.board[old_row][new_col]
                game_copy.board[old_row][new_col] = None
            
            # Move the piece
            game_copy.board[new_row][new_col] = piece
            game_copy.board[old_row][old_col] = None
            piece.position = move
            piece.has_moved = True
            
            # Update last move
            last_move = {
                'piece': piece,
                'from': (old_row, old_col),
                'to': move,
                'captured': captured_piece
            }
            
            # Switch turns
            game_copy.turn = game_copy.turn.opposite
            
            # Evaluate the move
            score = -self.minimax(game_copy, depth - 1, -beta, -alpha, False, last_move)
            
            # Restore the state
            game_copy.board[old_row][old_col] = piece
            game_copy.board[new_row][new_col] = captured_piece
            if piece.type == PieceType.PAWN and old_col != new_col and not captured_piece:
                game_copy.board[old_row][new_col] = last_move['captured']
            piece.position = (old_row, old_col)
            game_copy.turn = game_copy.turn.opposite
            
            if score > best_score:
                best_score = score
                best_move = (piece, move)
            
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        
        return best_move
    
    def minimax(self, game, depth, alpha, beta, maximizing, last_move):
        # If we've reached the maximum depth or the game is over, evaluate the board
        if depth == 0 or game.is_game_over():
            return self.evaluate_board(game)
        
        if maximizing:
            max_eval = float('-inf')
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    piece = game.board[row][col]
                    if piece and piece.color == game.turn:
                        moves = piece.get_possible_moves(game.board, last_move)
                        for move in moves:
                            # Make the move
                            old_row, old_col = piece.position
                            new_row, new_col = move
                            
                            # Save the state
                            captured_piece = game.board[new_row][new_col]
                            
                            # Handle en passant capture
                            if piece.type == PieceType.PAWN and old_col != new_col and not captured_piece:
                                # This is an en passant capture
                                captured_piece = game.board[old_row][new_col]
                                game.board[old_row][new_col] = None
                            
                            # Move the piece
                            game.board[new_row][new_col] = piece
                            game.board[old_row][old_col] = None
                            piece.position = move
                            piece.has_moved = True
                            
                            # Update last move
                            new_last_move = {
                                'piece': piece,
                                'from': (old_row, old_col),
                                'to': move,
                                'captured': captured_piece
                            }
                            
                            # Switch turns
                            game.turn = game.turn.opposite
                            
                            # Evaluate the move
                            eval = self.minimax(game, depth - 1, alpha, beta, False, new_last_move)
                            
                            # Restore the state
                            game.board[old_row][old_col] = piece
                            game.board[new_row][new_col] = captured_piece
                            if piece.type == PieceType.PAWN and old_col != new_col and not captured_piece:
                                game.board[old_row][new_col] = new_last_move['captured']
                            piece.position = (old_row, old_col)
                            game.turn = game.turn.opposite
                            
                            max_eval = max(max_eval, eval)
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            
            return max_eval
        else:
            min_eval = float('inf')
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    piece = game.board[row][col]
                    if piece and piece.color == game.turn:
                        moves = piece.get_possible_moves(game.board, last_move)
                        for move in moves:
                            # Make the move
                            old_row, old_col = piece.position
                            new_row, new_col = move
                            
                            # Save the state
                            captured_piece = game.board[new_row][new_col]
                            
                            # Handle en passant capture
                            if piece.type == PieceType.PAWN and old_col != new_col and not captured_piece:
                                # This is an en passant capture
                                captured_piece = game.board[old_row][new_col]
                                game.board[old_row][new_col] = None
                            
                            # Move the piece
                            game.board[new_row][new_col] = piece
                            game.board[old_row][old_col] = None
                            piece.position = move
                            piece.has_moved = True
                            
                            # Update last move
                            new_last_move = {
                                'piece': piece,
                                'from': (old_row, old_col),
                                'to': move,
                                'captured': captured_piece
                            }
                            
                            # Switch turns
                            game.turn = game.turn.opposite
                            
                            # Evaluate the move
                            eval = self.minimax(game, depth - 1, alpha, beta, True, new_last_move)
                            
                            # Restore the state
                            game.board[old_row][old_col] = piece
                            game.board[new_row][new_col] = captured_piece
                            if piece.type == PieceType.PAWN and old_col != new_col and not captured_piece:
                                game.board[old_row][new_col] = new_last_move['captured']
                            piece.position = (old_row, old_col)
                            game.turn = game.turn.opposite
                            
                            min_eval = min(min_eval, eval)
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            
            return min_eval
    
    def evaluate_board(self, game):
        score = 0
        
        # Count material
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = game.board[row][col]
                if piece:
                    # Material value
                    piece_value = self.piece_values[piece.type]
                    
                    # Position value (flipped for black)
                    position_table = self.position_values[piece.type]
                    position_row = row if piece.color == Color.BLACK else 7 - row
                    position_value = position_table[position_row][col]
                    
                    # Add to score (positive for AI, negative for opponent)
                    value = piece_value + position_value
                    if piece.color == game.turn:
                        score += value
                    else:
                        score -= value
        
        return score

class ChessGame:
    def __init__(self, mode=GameMode.PLAYER_VS_PLAYER, ai_difficulty=AIDifficulty.MEDIUM):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = Color.WHITE
        self.selected_piece = None
        self.possible_moves = []
        self.game_over = False
        self.winner = None
        self.mode = mode
        self.ai = ChessAI(ai_difficulty)
        self.ai_thinking = False
        self.move_history = []
        self.last_move = None
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.create_piece_images()
        self.setup_board()
        self.create_buttons()
    
    def create_piece_images(self):
        """Create realistic chess piece images that look like traditional Staunton chess pieces"""
        piece_size = SQUARE_SIZE - 8
        
        # Define colors for pieces - more realistic chess piece colors
        white_color = (252, 252, 252)    # Pure white pieces
        black_color = (35, 35, 35)       # Deep black pieces
        white_outline = (180, 180, 180)  # Light gray outline
        black_outline = (10, 10, 10)     # Very dark outline
        white_highlight = (255, 255, 255)  # White highlight
        black_highlight = (60, 60, 60)     # Dark highlight
        
        # Create images for each piece type using traditional Staunton design
        for color in [Color.WHITE, Color.BLACK]:
            piece_color = white_color if color == Color.WHITE else black_color
            outline_color = white_outline if color == Color.WHITE else black_outline
            
            # PAWN - Traditional rounded head with tapered body
            pawn_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            center_x = piece_size // 2
            
            # Base (wide oval)
            base_rect = (piece_size//4, piece_size*4//5, piece_size//2, piece_size//8)
            pygame.draw.ellipse(pawn_img, piece_color, base_rect)
            pygame.draw.ellipse(pawn_img, outline_color, base_rect, 2)
            
            # Stem (tapered body)
            stem_points = [
                (center_x - piece_size//10, piece_size*4//5),
                (center_x + piece_size//10, piece_size*4//5),
                (center_x + piece_size//12, piece_size*2//5),
                (center_x - piece_size//12, piece_size*2//5)
            ]
            pygame.draw.polygon(pawn_img, piece_color, stem_points)
            pygame.draw.polygon(pawn_img, outline_color, stem_points, 2)
            
            # Collar (small ring)
            collar_rect = (center_x - piece_size//8, piece_size*2//5, piece_size//4, piece_size//12)
            pygame.draw.ellipse(pawn_img, piece_color, collar_rect)
            pygame.draw.ellipse(pawn_img, outline_color, collar_rect, 2)
            
            # Head (perfect circle)
            head_radius = piece_size // 8
            pygame.draw.circle(pawn_img, piece_color, (center_x, piece_size//4), head_radius)
            pygame.draw.circle(pawn_img, outline_color, (center_x, piece_size//4), head_radius, 2)
            
            IMAGES[f"{color.value}p"] = pawn_img
            
            # KNIGHT - Stylized horse head in profile (Staunton style)
            knight_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            
            # Base
            base_rect = (piece_size//4, piece_size*4//5, piece_size//2, piece_size//8)
            pygame.draw.ellipse(knight_img, piece_color, base_rect)
            pygame.draw.ellipse(knight_img, outline_color, base_rect, 2)
            
            # Horse head profile (complex shape)
            head_points = [
                # Neck/base connection
                (center_x - piece_size//8, piece_size*4//5),
                (center_x + piece_size//8, piece_size*4//5),
                # Chest
                (center_x + piece_size//6, piece_size*3//5),
                # Nose/muzzle
                (center_x + piece_size//4, piece_size*2//5),
                (center_x + piece_size//5, piece_size//3),
                # Forehead
                (center_x + piece_size//8, piece_size//4),
                # Ears
                (center_x, piece_size//6),
                (center_x - piece_size//12, piece_size//5),
                # Back of head/mane
                (center_x - piece_size//6, piece_size//3),
                # Neck back
                (center_x - piece_size//5, piece_size//2),
                (center_x - piece_size//8, piece_size*3//5)
            ]
            pygame.draw.polygon(knight_img, piece_color, head_points)
            pygame.draw.polygon(knight_img, outline_color, head_points, 2)
            
            # Eye
            eye_pos = (center_x + piece_size//12, piece_size//3)
            pygame.draw.circle(knight_img, outline_color, eye_pos, 2)
            
            # Nostril
            nostril_pos = (center_x + piece_size//6, piece_size*2//5)
            pygame.draw.circle(knight_img, outline_color, nostril_pos, 1)
            
            # Mane details
            mane_lines = [
                ((center_x - piece_size//8, piece_size//4), (center_x - piece_size//12, piece_size//6)),
                ((center_x - piece_size//10, piece_size//3), (center_x - piece_size//16, piece_size//5)),
                ((center_x - piece_size//12, piece_size*2//5), (center_x, piece_size//4))
            ]
            for start, end in mane_lines:
                pygame.draw.line(knight_img, outline_color, start, end, 2)
            
            IMAGES[f"{color.value}n"] = knight_img
            
            # BISHOP - Traditional mitre with cross
            bishop_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            
            # Base
            base_rect = (piece_size//4, piece_size*4//5, piece_size//2, piece_size//8)
            pygame.draw.ellipse(bishop_img, piece_color, base_rect)
            pygame.draw.ellipse(bishop_img, outline_color, base_rect, 2)
            
            # Body (tapered)
            body_points = [
                (center_x - piece_size//8, piece_size*4//5),
                (center_x + piece_size//8, piece_size*4//5),
                (center_x + piece_size//10, piece_size*2//5),
                (center_x - piece_size//10, piece_size*2//5)
            ]
            pygame.draw.polygon(bishop_img, piece_color, body_points)
            pygame.draw.polygon(bishop_img, outline_color, body_points, 2)
            
            # Collar
            collar_rect = (center_x - piece_size//6, piece_size*2//5, piece_size//3, piece_size//12)
            pygame.draw.ellipse(bishop_img, piece_color, collar_rect)
            pygame.draw.ellipse(bishop_img, outline_color, collar_rect, 2)
            
            # Mitre (bishop's hat) - pointed oval
            mitre_points = [
                (center_x, piece_size//8),  # Top point
                (center_x - piece_size//8, piece_size//3),  # Left base
                (center_x + piece_size//8, piece_size//3),  # Right base
            ]
            pygame.draw.polygon(bishop_img, piece_color, mitre_points)
            pygame.draw.polygon(bishop_img, outline_color, mitre_points, 2)
            
            # Cross on mitre
            cross_center = (center_x, piece_size//5)
            cross_size = piece_size // 16
            # Vertical line
            pygame.draw.line(bishop_img, outline_color,
                           (cross_center[0], cross_center[1] - cross_size),
                           (cross_center[0], cross_center[1] + cross_size), 3)
            # Horizontal line
            pygame.draw.line(bishop_img, outline_color,
                           (cross_center[0] - cross_size//2, cross_center[1]),
                           (cross_center[0] + cross_size//2, cross_center[1]), 3)
            
            # Split line in mitre (traditional detail)
            pygame.draw.line(bishop_img, outline_color,
                           (center_x, piece_size//6),
                           (center_x, piece_size//3), 2)
            
            IMAGES[f"{color.value}b"] = bishop_img
            
            # ROOK - Castle turret with crenellations
            rook_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            
            # Base
            base_rect = (piece_size//4, piece_size*4//5, piece_size//2, piece_size//8)
            pygame.draw.ellipse(rook_img, piece_color, base_rect)
            pygame.draw.ellipse(rook_img, outline_color, base_rect, 2)
            
            # Main tower body
            tower_rect = (center_x - piece_size//6, piece_size*2//5, piece_size//3, piece_size*2//5)
            pygame.draw.rect(rook_img, piece_color, tower_rect)
            pygame.draw.rect(rook_img, outline_color, tower_rect, 2)
            
            # Crenellations (castle battlements) - authentic pattern
            cren_width = piece_size // 12
            cren_height = piece_size // 8
            
            # Draw 5 crenellations with gaps
            for i in range(5):
                if i % 2 == 0:  # Solid merlons
                    cren_x = center_x - piece_size//6 + i * cren_width
                    cren_rect = (cren_x, piece_size//4, cren_width, cren_height)
                    pygame.draw.rect(rook_img, piece_color, cren_rect)
                    pygame.draw.rect(rook_img, outline_color, cren_rect, 2)
            
            # Horizontal band (decorative ring)
            band_rect = (center_x - piece_size//6, piece_size*3//5, piece_size//3, piece_size//16)
            pygame.draw.rect(rook_img, piece_color, band_rect)
            pygame.draw.rect(rook_img, outline_color, band_rect, 2)
            
            # Arrow slit (window)
            slit_rect = (center_x - 1, piece_size//2, 2, piece_size//8)
            pygame.draw.rect(rook_img, outline_color, slit_rect)
            
            IMAGES[f"{color.value}r"] = rook_img
            
            # QUEEN - Elaborate crown with multiple points
            queen_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            
            # Base
            base_rect = (piece_size//4, piece_size*4//5, piece_size//2, piece_size//8)
            pygame.draw.ellipse(queen_img, piece_color, base_rect)
            pygame.draw.ellipse(queen_img, outline_color, base_rect, 2)
            
            # Body (elegant curves)
            body_points = [
                (center_x - piece_size//8, piece_size*4//5),
                (center_x + piece_size//8, piece_size*4//5),
                (center_x + piece_size//6, piece_size*3//5),
                (center_x + piece_size//8, piece_size*2//5),
                (center_x - piece_size//8, piece_size*2//5),
                (center_x - piece_size//6, piece_size*3//5)
            ]
            pygame.draw.polygon(queen_img, piece_color, body_points)
            pygame.draw.polygon(queen_img, outline_color, body_points, 2)
            
            # Crown base (circlet)
            crown_base_rect = (center_x - piece_size//6, piece_size*2//5, piece_size//3, piece_size//12)
            pygame.draw.ellipse(queen_img, piece_color, crown_base_rect)
            pygame.draw.ellipse(queen_img, outline_color, crown_base_rect, 2)
            
            # Crown points (5 points of varying heights)
            crown_points = []
            num_points = 5
            base_y = piece_size * 2 // 5
            
            for i in range(num_points):
                x = center_x - piece_size//6 + (i * piece_size//15)
                if i == 2:  # Center point is tallest
                    y = piece_size // 6
                elif i == 1 or i == 3:  # Side points medium height
                    y = piece_size // 5
                else:  # Outer points shortest
                    y = piece_size // 4
                
                # Draw individual crown point
                point_shape = [
                    (x, base_y),
                    (x + piece_size//20, base_y),
                    (x + piece_size//40, y),
                    (x - piece_size//40, y)
                ]
                pygame.draw.polygon(queen_img, piece_color, point_shape)
                pygame.draw.polygon(queen_img, outline_color, point_shape, 2)
                
                # Add jewel at tip
                jewel_color = GOLD if color == Color.WHITE else SILVER
                pygame.draw.circle(queen_img, jewel_color, (x, y), piece_size//30)
                pygame.draw.circle(queen_img, outline_color, (x, y), piece_size//30, 1)
            
            IMAGES[f"{color.value}q"] = queen_img
            
            # KING - Royal crown with cross finial
            king_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            
            # Base
            base_rect = (piece_size//4, piece_size*4//5, piece_size//2, piece_size//8)
            pygame.draw.ellipse(king_img, piece_color, base_rect)
            pygame.draw.ellipse(king_img, outline_color, base_rect, 2)
            
            # Body (royal proportions)
            body_points = [
                (center_x - piece_size//8, piece_size*4//5),
                (center_x + piece_size//8, piece_size*4//5),
                (center_x + piece_size//6, piece_size*3//5),
                (center_x + piece_size//8, piece_size*2//5),
                (center_x - piece_size//8, piece_size*2//5),
                (center_x - piece_size//6, piece_size*3//5)
            ]
            pygame.draw.polygon(king_img, piece_color, body_points)
            pygame.draw.polygon(king_img, outline_color, body_points, 2)
            
            # Crown base (band)
            crown_band_rect = (center_x - piece_size//5, piece_size*2//5, piece_size*2//5, piece_size//10)
            pygame.draw.ellipse(king_img, piece_color, crown_band_rect)
            pygame.draw.ellipse(king_img, outline_color, crown_band_rect, 2)
            
            # Crown arches (4 distinctive arches)
            arch_centers = [
                (center_x - piece_size//8, piece_size//3),
                (center_x - piece_size//16, piece_size//4),
                (center_x + piece_size//16, piece_size//4),
                (center_x + piece_size//8, piece_size//3)
            ]
            
            for i, (x, y) in enumerate(arch_centers):
                if i == 1 or i == 2:  # Center arches are higher
                    arch_height = piece_size // 12
                else:  # Side arches are lower
                    arch_height = piece_size // 16
                
                arch_rect = (x - piece_size//24, y, piece_size//12, arch_height)
                pygame.draw.ellipse(king_img, piece_color, arch_rect)
                pygame.draw.ellipse(king_img, outline_color, arch_rect, 2)
            
            # Cross finial (traditional king's cross)
            cross_center = (center_x, piece_size//6)
            cross_size = piece_size // 12
            
            # Vertical beam
            pygame.draw.line(king_img, outline_color,
                           (cross_center[0], cross_center[1] - cross_size),
                           (cross_center[0], cross_center[1] + cross_size), 4)
            # Horizontal beam
            pygame.draw.line(king_img, outline_color,
                           (cross_center[0] - cross_size//2, cross_center[1] - cross_size//3),
                           (cross_center[0] + cross_size//2, cross_center[1] - cross_size//3), 4)
            
            # Royal orb (jewel at cross center)
            jewel_color = GOLD if color == Color.WHITE else SILVER
            pygame.draw.circle(king_img, jewel_color, cross_center, piece_size//25)
            pygame.draw.circle(king_img, outline_color, cross_center, piece_size//25, 2)
            
            IMAGES[f"{color.value}k"] = king_img
            # Crown jewels
            jewel_color = GOLD if color == Color.WHITE else SILVER
            for i, x in enumerate([piece_size//3 + piece_size//12, piece_size//2, piece_size*2//3 - piece_size//12]):
                y = piece_size//5 if i == 1 else piece_size//4
                pygame.draw.circle(queen_img, jewel_color, (x, y), piece_size//20)
                pygame.draw.circle(queen_img, outline_color, (x, y), piece_size//20, 2)
            # Body
            pygame.draw.polygon(queen_img, piece_color, [
                (piece_size//3, piece_size//3),
                (piece_size*2//3, piece_size//3),
                (piece_size*2//3 + piece_size//12, piece_size*2//3),
                (piece_size//3 - piece_size//12, piece_size*2//3)
            ])
            pygame.draw.polygon(queen_img, outline_color, [
                (piece_size//3, piece_size//3),
                (piece_size*2//3, piece_size//3),
                (piece_size*2//3 + piece_size//12, piece_size*2//3),
                (piece_size//3 - piece_size//12, piece_size*2//3)
            ], 3)
            # Base
            pygame.draw.ellipse(queen_img, piece_color,
                               (piece_size//5, piece_size*2//3, piece_size*3//5, piece_size//6))
            pygame.draw.ellipse(queen_img, outline_color,
                               (piece_size//5, piece_size*2//3, piece_size*3//5, piece_size//6), 3)
            IMAGES[f"{color.value}q"] = queen_img
            
            # King - Crown with cross
            king_img = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA)
            # Crown base
            crown_rect = (piece_size//3, piece_size//4, piece_size//3, piece_size//8)
            pygame.draw.rect(king_img, piece_color, crown_rect)
            pygame.draw.rect(king_img, outline_color, crown_rect, 3)
            # Cross on crown
            cross_center = (piece_size//2, piece_size//5)
            pygame.draw.line(king_img, outline_color,
                           (cross_center[0], cross_center[1] - piece_size//12),
                           (cross_center[0], cross_center[1] + piece_size//12), 4)
            pygame.draw.line(king_img, outline_color,
                           (cross_center[0] - piece_size//16, cross_center[1]),
                           (cross_center[0] + piece_size//16, cross_center[1]), 4)
            # Crown jewel
            jewel_color = GOLD if color == Color.WHITE else SILVER
            pygame.draw.circle(king_img, jewel_color, cross_center, piece_size//24)
            pygame.draw.circle(king_img, outline_color, cross_center, piece_size//24, 2)
            # Body
            pygame.draw.polygon(king_img, piece_color, [
                (piece_size//3, piece_size//3),
                (piece_size*2//3, piece_size//3),
                (piece_size*2//3 + piece_size//12, piece_size*2//3),
                (piece_size//3 - piece_size//12, piece_size*2//3)
            ])
            pygame.draw.polygon(king_img, outline_color, [
                (piece_size//3, piece_size//3),
                (piece_size*2//3, piece_size//3),
                (piece_size*2//3 + piece_size//12, piece_size*2//3),
                (piece_size//3 - piece_size//12, piece_size*2//3)
            ], 3)
            # Base
            pygame.draw.ellipse(king_img, piece_color,
                               (piece_size//5, piece_size*2//3, piece_size*3//5, piece_size//6))
            pygame.draw.ellipse(king_img, outline_color,
                               (piece_size//5, piece_size*2//3, piece_size*3//5, piece_size//6), 3)
            IMAGES[f"{color.value}k"] = king_img

    
    def create_buttons(self):
        self.buttons = []
        
        # Game mode buttons
        self.buttons.append(Button(WINDOW_SIZE + 20, 20, 160, 30, "Player vs Player", 
                                  lambda: self.set_game_mode(GameMode.PLAYER_VS_PLAYER)))
        self.buttons.append(Button(WINDOW_SIZE + 20, 60, 160, 30, "Player vs AI", 
                                  lambda: self.set_game_mode(GameMode.PLAYER_VS_AI)))
        
        # AI difficulty buttons
        self.buttons.append(Button(WINDOW_SIZE + 20, 120, 160, 30, "Easy AI", 
                                  lambda: self.set_ai_difficulty(AIDifficulty.EASY)))
        self.buttons.append(Button(WINDOW_SIZE + 20, 160, 160, 30, "Medium AI", 
                                  lambda: self.set_ai_difficulty(AIDifficulty.MEDIUM)))
        self.buttons.append(Button(WINDOW_SIZE + 20, 200, 160, 30, "Hard AI", 
                                  lambda: self.set_ai_difficulty(AIDifficulty.HARD)))
        self.buttons.append(Button(WINDOW_SIZE + 20, 240, 160, 30, "Expert AI", 
                                  lambda: self.set_ai_difficulty(AIDifficulty.EXPERT)))
        
        # New game button
        self.buttons.append(Button(WINDOW_SIZE + 20, 300, 160, 30, "New Game", self.new_game))
    
    def set_game_mode(self, mode):
        self.mode = mode
        self.new_game()
    
    def set_ai_difficulty(self, difficulty):
        self.ai.difficulty = difficulty
        if self.mode == GameMode.PLAYER_VS_AI:
            self.new_game()
    
    def new_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = Color.WHITE
        self.selected_piece = None
        self.possible_moves = []
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.last_move = None
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.setup_board()
    
    def setup_board(self):
        # Set up pawns
        for col in range(BOARD_SIZE):
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK, (1, col))
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE, (6, col))
        
        # Set up other pieces
        back_row = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        for col, piece_type in enumerate(back_row):
            self.board[0][col] = Piece(piece_type, Color.BLACK, (0, col))
            self.board[7][col] = Piece(piece_type, Color.WHITE, (7, col))
    
    def handle_click(self, pos):
        # Check if a button was clicked
        for button in self.buttons:
            if button.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': pos, 'button': 1})):
                return
        
        # If AI is thinking or game is over, ignore clicks on the board
        if self.ai_thinking or self.game_over or pos[0] >= WINDOW_SIZE:
            return
        
        # If it's AI's turn in Player vs AI mode, ignore clicks
        if self.mode == GameMode.PLAYER_VS_AI and self.turn == Color.BLACK:
            return
        
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        
        # If a piece is already selected
        if self.selected_piece:
            # If clicked on a possible move
            if (row, col) in self.possible_moves:
                self.move_piece(self.selected_piece, (row, col))
                self.selected_piece = None
                self.possible_moves = []
                
                # If in Player vs AI mode and it's AI's turn, make AI move
                if self.mode == GameMode.PLAYER_VS_AI and self.turn == Color.BLACK and not self.game_over:
                    self.ai_thinking = True
            else:
                # If clicked on another piece of the same color
                if self.board[row][col] is not None and self.board[row][col].color == self.turn:
                    self.selected_piece = self.board[row][col]
                    self.possible_moves = self.selected_piece.get_possible_moves(self.board, self.last_move)
                else:
                    self.selected_piece = None
                    self.possible_moves = []
        else:
            # Select a piece
            if self.board[row][col] is not None and self.board[row][col].color == self.turn:
                self.selected_piece = self.board[row][col]
                self.possible_moves = self.selected_piece.get_possible_moves(self.board, self.last_move)
    
    def move_piece(self, piece, new_pos):
        old_row, old_col = piece.position
        new_row, new_col = new_pos
        
        # Record the move
        captured = self.board[new_row][new_col]
        
        # Handle en passant capture
        if piece.type == PieceType.PAWN and old_col != new_col and not captured:
            # This is an en passant capture
            captured = self.board[old_row][new_col]
            self.board[old_row][new_col] = None
        
        self.last_move = {
            'piece': piece,
            'from': (old_row, old_col),
            'to': new_pos,
            'captured': captured
        }
        
        self.move_history.append(self.last_move)
        
        # Check for castling
        if piece.type == PieceType.KING and abs(old_col - new_col) > 1:
            # Kingside castling
            if new_col > old_col:
                rook = self.board[old_row][7]
                self.board[old_row][5] = rook
                self.board[old_row][7] = None
                rook.position = (old_row, 5)
                rook.has_moved = True
            # Queenside castling
            else:
                rook = self.board[old_row][0]
                self.board[old_row][3] = rook
                self.board[old_row][0] = None
                rook.position = (old_row, 3)
                rook.has_moved = True
        
        # Check for pawn promotion
        if piece.type == PieceType.PAWN and (new_row == 0 or new_row == 7):
            piece.type = PieceType.QUEEN
            piece.image_key = f"{piece.color.value}q"
        
        # Move the piece
        self.board[new_row][new_col] = piece
        self.board[old_row][old_col] = None
        piece.position = new_pos
        piece.has_moved = True
        
        # Switch turns
        self.turn = self.turn.opposite
        
        # Check for check, checkmate, or stalemate
        self.check_game_state()
    
    def make_ai_move(self):
        # Get the AI's move
        ai_move = self.ai.get_move(self)
        
        if ai_move:
            piece, move = ai_move
            self.move_piece(piece, move)
        else:
            # If AI can't move, it's either checkmate or stalemate
            self.game_over = True
        
        self.ai_thinking = False
    
    def is_game_over(self):
        return self.game_over
    
    def check_game_state(self):
        """Check if the current player is in check, checkmate, or stalemate"""
        # Find the king
        king = None
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == self.turn:
                    king = piece
                    break
            if king:
                break
        
        # Check if the king is in check
        self.in_check = king.is_in_check(self.board)
        
        # Check if the player has any legal moves
        has_legal_moves = False
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.color == self.turn:
                    moves = piece.get_possible_moves(self.board, self.last_move)
                    if moves:
                        has_legal_moves = True
                        break
            if has_legal_moves:
                break
        
        # If no legal moves, it's either checkmate or stalemate
        if not has_legal_moves:
            self.game_over = True
            if self.in_check:
                self.checkmate = True
                self.winner = self.turn.opposite
            else:
                self.stalemate = True
                self.winner = None
    
    def draw(self, screen):
        # Draw the board with border and coordinates
        board_rect = (10, 10, WINDOW_SIZE - 20, WINDOW_SIZE - 20)
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WINDOW_SIZE, WINDOW_SIZE))
        pygame.draw.rect(screen, LIGHT_SQUARE, board_rect)
        
        # Draw coordinate labels
        font = pygame.font.SysFont('Times New Roman', 16, bold=True)
        
        # Draw files (a-h) at bottom
        for col in range(BOARD_SIZE):
            file_label = chr(ord('a') + col)
            text = font.render(file_label, True, BORDER_COLOR)
            x = col * SQUARE_SIZE + SQUARE_SIZE//2 - text.get_width()//2
            y = WINDOW_SIZE - 25
            screen.blit(text, (x, y))
        
        # Draw ranks (1-8) on left side
        for row in range(BOARD_SIZE):
            rank_label = str(8 - row)
            text = font.render(rank_label, True, BORDER_COLOR)
            x = 5
            y = row * SQUARE_SIZE + SQUARE_SIZE//2 - text.get_height()//2
            screen.blit(text, (x, y))
        
        # Draw the squares with subtle gradient effect
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE
                
                # Base square color
                if (row + col) % 2 == 0:
                    base_color = LIGHT_SQUARE
                    shadow_color = tuple(max(0, c - 20) for c in LIGHT_SQUARE)
                else:
                    base_color = DARK_SQUARE
                    shadow_color = tuple(max(0, c - 20) for c in DARK_SQUARE)
                
                # Draw square with subtle 3D effect
                square_rect = (x, y, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, base_color, square_rect)
                
                # Add subtle border for depth
                pygame.draw.line(screen, shadow_color, (x, y + SQUARE_SIZE - 1), (x + SQUARE_SIZE - 1, y + SQUARE_SIZE - 1), 1)
                pygame.draw.line(screen, shadow_color, (x + SQUARE_SIZE - 1, y), (x + SQUARE_SIZE - 1, y + SQUARE_SIZE - 1), 1)
                
                # Highlight selected piece with golden glow
                if self.selected_piece and self.selected_piece.position == (row, col):
                    glow_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    glow_surface.fill(HIGHLIGHT)
                    screen.blit(glow_surface, (x, y))
                    # Add golden border
                    pygame.draw.rect(screen, GOLD, square_rect, 4)
                
                # Highlight possible moves with green dots and subtle glow
                if (row, col) in self.possible_moves:
                    move_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    move_surface.fill(MOVE_HIGHLIGHT)
                    screen.blit(move_surface, (x, y))
                    # Draw a green circle in the center
                    circle_center = (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2)
                    pygame.draw.circle(screen, (34, 139, 34), circle_center, SQUARE_SIZE//6)
                    pygame.draw.circle(screen, (0, 100, 0), circle_center, SQUARE_SIZE//6, 3)
                
                # Highlight king in check with pulsing red effect
                piece = self.board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == self.turn and self.in_check:
                    check_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    check_surface.fill(CHECK_HIGHLIGHT)
                    screen.blit(check_surface, (x, y))
                    # Add red border
                    pygame.draw.rect(screen, (220, 20, 60), square_rect, 5)
                
                # Highlight last move with orange glow
                if self.last_move:
                    last_from = self.last_move['from']
                    last_to = self.last_move['to']
                    if (row, col) == last_from or (row, col) == last_to:
                        last_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        last_surface.fill(LAST_MOVE_HIGHLIGHT)
                        screen.blit(last_surface, (x, y))
                
                # Draw pieces with shadow effect
                if piece:
                    img = IMAGES[piece.image_key]
                    # Draw shadow first
                    shadow_offset = 2
                    shadow_surface = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    shadow_surface.fill((0, 0, 0, 50))
                    shadow_rect = img.get_rect(center=(x + SQUARE_SIZE//2 + shadow_offset, y + SQUARE_SIZE//2 + shadow_offset))
                    screen.blit(shadow_surface, shadow_rect)
                    # Draw the piece
                    img_rect = img.get_rect(center=(x + SQUARE_SIZE//2, y + SQUARE_SIZE//2))
                    screen.blit(img, img_rect)
        
        # Draw elegant sidebar with wood texture effect
        sidebar_rect = (WINDOW_SIZE, 0, SIDEBAR_WIDTH, WINDOW_SIZE)
        pygame.draw.rect(screen, SIDEBAR_BG, sidebar_rect)
        # Add wood grain lines
        for i in range(0, WINDOW_SIZE, 20):
            line_color = tuple(min(255, c + 10) for c in SIDEBAR_BG)
            pygame.draw.line(screen, line_color, (WINDOW_SIZE, i), (WINDOW_SIZE + SIDEBAR_WIDTH, i), 1)
        
        # Add vertical border
        pygame.draw.line(screen, BORDER_COLOR, (WINDOW_SIZE, 0), (WINDOW_SIZE, WINDOW_SIZE), 3)
        
        # Draw buttons with improved styling
        for button in self.buttons:
            button.draw(screen)
        
        # Draw game info with elegant typography
        title_font = pygame.font.SysFont('Times New Roman', 24, bold=True)
        info_font = pygame.font.SysFont('Times New Roman', 18)
        small_font = pygame.font.SysFont('Times New Roman', 14)
        
        # Title
        title_text = "Made by jihad"
        title_surf = title_font.render(title_text, True, GOLD)
        title_rect = title_surf.get_rect(centerx=WINDOW_SIZE + SIDEBAR_WIDTH//2, y=10)
        screen.blit(title_surf, title_rect)
        
        # Current turn with icon
        turn_color = "White" if self.turn == Color.WHITE else "Black"
        turn_text = f"Turn: {turn_color}"
        turn_surf = info_font.render(turn_text, True, TEXT_COLOR)
        screen.blit(turn_surf, (WINDOW_SIZE + 20, 350))
        
        # Draw a small piece icon next to turn
        if self.turn == Color.WHITE:
            icon_color = (248, 248, 255)
        else:
            icon_color = (47, 79, 79)
        pygame.draw.circle(screen, icon_color, (WINDOW_SIZE + 160, 360), 8)
        pygame.draw.circle(screen, TEXT_COLOR, (WINDOW_SIZE + 160, 360), 8, 2)
        
        # Check status with dramatic styling
        if self.in_check:
            check_text = "⚠ CHECK! ⚠"
            check_surf = title_font.render(check_text, True, (255, 69, 0))
            check_rect = check_surf.get_rect(centerx=WINDOW_SIZE + SIDEBAR_WIDTH//2, y=380)
            screen.blit(check_surf, check_rect)
        
        # Game mode
        mode_text = f"Mode: {'Player vs Player' if self.mode == GameMode.PLAYER_VS_PLAYER else 'Player vs AI'}"
        mode_surf = small_font.render(mode_text, True, TEXT_COLOR)
        screen.blit(mode_surf, (WINDOW_SIZE + 20, 410))
        
        # AI difficulty if in PvAI mode
        if self.mode == GameMode.PLAYER_VS_AI:
            diff_text = f"AI Level: {self.ai.difficulty.name}"
            diff_surf = small_font.render(diff_text, True, TEXT_COLOR)
            screen.blit(diff_surf, (WINDOW_SIZE + 20, 430))
        
        # AI thinking message with animation dots
        if self.ai_thinking:
            import time
            dots = "." * (int(time.time() * 2) % 4)
            thinking_text = f"AI thinking{dots}"
            thinking_surf = info_font.render(thinking_text, True, GOLD)
            screen.blit(thinking_surf, (WINDOW_SIZE + 20, 460))
        
        # Last move in chess notation
        if self.last_move:
            from_row, from_col = self.last_move['from']
            to_row, to_col = self.last_move['to']
            piece_symbol = {'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'}
            piece_char = piece_symbol.get(self.last_move['piece'].type.value, '')
            last_move_text = f"Last: {piece_char}{chr(97+from_col)}{8-from_row}→{chr(97+to_col)}{8-to_row}"
            last_move_surf = small_font.render(last_move_text, True, TEXT_COLOR)
            screen.blit(last_move_surf, (WINDOW_SIZE + 20, 490))
        
        # Move count
        move_count = len(self.move_history)
        move_text = f"Moves: {move_count//2 + 1}"
        move_surf = small_font.render(move_text, True, TEXT_COLOR)
        screen.blit(move_surf, (WINDOW_SIZE + 20, 510))
        
        # Game over message with elegant styling
        if self.game_over:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            # Main message
            game_over_font = pygame.font.SysFont('Times New Roman', 48, bold=True)
            if self.checkmate:
                winner_name = "White" if self.winner == Color.WHITE else "Black"
                main_text = f"Checkmate!"
                sub_text = f"{winner_name} Wins!"
                text_color = GOLD
            elif self.stalemate:
                main_text = "Stalemate!"
                sub_text = "Draw Game"
                text_color = SILVER
            else:
                main_text = "Game Over!"
                sub_text = ""
                text_color = TEXT_COLOR
            
            # Draw main text
            main_surf = game_over_font.render(main_text, True, text_color)
            main_rect = main_surf.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 30))
            
            # Draw background for text
            bg_rect = main_rect.inflate(40, 80)
            pygame.draw.rect(screen, SIDEBAR_BG, bg_rect)
            pygame.draw.rect(screen, BORDER_COLOR, bg_rect, 5)
            
            screen.blit(main_surf, main_rect)
            
            # Draw sub text
            if sub_text:
                sub_font = pygame.font.SysFont('Times New Roman', 24)
                sub_surf = sub_font.render(sub_text, True, text_color)
                sub_rect = sub_surf.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 20))
                screen.blit(sub_surf, sub_rect)

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_SIZE))
    pygame.display.set_caption("Made by jihad")
    
    game = ChessGame(mode=GameMode.PLAYER_VS_PLAYER)
    
    mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    game.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                # Update button hover states
                for button in game.buttons:
                    button.check_hover(mouse_pos)
        
        # Make AI move if it's AI's turn
        if game.mode == GameMode.PLAYER_VS_AI and game.turn == Color.BLACK and not game.game_over and game.ai_thinking:
            game.make_ai_move()
        
        # Schedule AI to think on the next frame if it's AI's turn
        if game.mode == GameMode.PLAYER_VS_AI and game.turn == Color.BLACK and not game.game_over and not game.ai_thinking:
            game.ai_thinking = True
        
        # Draw everything
        screen.fill(pure_white)
        game.draw(screen)
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()