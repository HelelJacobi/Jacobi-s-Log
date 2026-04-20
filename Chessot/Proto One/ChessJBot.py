# -*- coding: utf-8 -*-
"""
Advanced Chess Engine with Learning Capabilities
Features: Minimax with Alpha-Beta Pruning, Transposition Table, Learning System
"""
import chess
import json
import os
from pathlib import Path
from typing import Tuple, Optional, Dict
import random

class LearningChessBot:
    """Chess engine with learning capabilities that improves over time"""
    
    def __init__(self, skill_level: int = 1, learning_file: str = "bot_knowledge.json"):
        """
        Initialize the bot
        skill_level: 1-4 (1=easy, 4=hard)
        """
        self.skill_level = max(1, min(4, skill_level))
        self.max_depth = self.skill_level * 2
        self.transposition_table: Dict = {}
        self.learning_file = learning_file
        self.player_patterns_file = "player_patterns.json"
        self.learned_positions = self._load_knowledge()
        self.player_patterns = self._load_player_patterns()
        self.opening_book = self._init_opening_book()
        
        # Advanced evaluation parameters
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000,
        }
        
        # Piece-square tables for positional play
        self.pawn_table = [
            0, 0, 0, 0, 0, 0, 0, 0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5, 5, 10, 25, 25, 10, 5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, -5, -10, 0, 0, -10, -5, 5,
            5, 10, 10, -20, -20, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        
        self.knight_table = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ]
        
        self.bishop_table = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ]
        
        self.rook_table = [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, 10, 10, 10, 10, 5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            0, 0, 0, 5, 5, 0, 0, 0
        ]
        
        self.queen_table = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -5, 0, 5, 5, 5, 5, 0, -5,
            0, 0, 5, 5, 5, 5, 0, -5,
            -10, 5, 5, 5, 5, 5, 0, -10,
            -10, 0, 5, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ]
        
        self.king_table = [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20, 20, 0, 0, 0, 0, 20, 20,
            20, 30, 10, 0, 0, 10, 30, 20
        ]

    def _init_opening_book(self) -> Dict:
        """Initialize opening book with common opening moves"""
        opening_book = {}
        
        # Starting position - White's first moves
        board = chess.Board()
        # e4 (Italian Game, Ruy Lopez)
        opening_book[board.fen()] = [chess.Move.from_uci("e2e4")]
        
        # After 1.e4, common Black responses
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        opening_book[board.fen()] = [
            chess.Move.from_uci("e7e5"),  # Classical
            chess.Move.from_uci("c7c5"),  # Sicilian
        ]
        
        # 1.e4 e5 - White's common responses
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("e7e5"))
        opening_book[board.fen()] = [
            chess.Move.from_uci("g1f3"),  # Nf3
            chess.Move.from_uci("f1c4"),  # Italian
        ]
        
        # 1.e4 c5 (Sicilian) - White's moves
        board = chess.Board()
        board.push(chess.Move.from_uci("e2e4"))
        board.push(chess.Move.from_uci("c7c5"))
        opening_book[board.fen()] = [
            chess.Move.from_uci("g1f3"),  # Nf3
            chess.Move.from_uci("d2d4"),  # d4
        ]
        
        # 1.d4 - Queen's Gambit and others
        board = chess.Board()
        board.push(chess.Move.from_uci("d2d4"))
        opening_book[board.fen()] = [
            chess.Move.from_uci("d7d5"),  # Queen's Gambit
            chess.Move.from_uci("g8f6"),  # Nf6
        ]
        
        return opening_book

    def _load_knowledge(self) -> Dict:
        """Load previously learned positions"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_knowledge(self):
        """Save learned positions to file"""
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.learned_positions, f)
        except Exception as e:
            print(f"Error saving knowledge: {e}")

    def _load_player_patterns(self) -> Dict:
        """Load player opening preferences and playstyle patterns"""
        if os.path.exists(self.player_patterns_file):
            try:
                with open(self.player_patterns_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_player_patterns(self):
        """Save player patterns to file"""
        try:
            with open(self.player_patterns_file, 'w') as f:
                json.dump(self.player_patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving player patterns: {e}")

    def learn_from_game(self, moves: list, result: str, player_color: int = chess.WHITE):
        """Learn from a completed game and track player patterns"""
        board = chess.Board()
        for i, move in enumerate(moves):
            fen = board.fen()
            is_player_move = (board.turn == player_color)
            
            # Track all positions
            if fen not in self.learned_positions:
                self.learned_positions[fen] = {"wins": 0, "losses": 0, "draws": 0}
            
            if result == "1-0":
                self.learned_positions[fen]["wins"] += 1
            elif result == "0-1":
                self.learned_positions[fen]["losses"] += 1
            else:
                self.learned_positions[fen]["draws"] += 1
            
            # Track player moves specifically for learning their playstyle
            if is_player_move:
                move_uci = move.uci()
                if fen not in self.player_patterns:
                    self.player_patterns[fen] = {}
                if move_uci not in self.player_patterns[fen]:
                    self.player_patterns[fen][move_uci] = {"count": 0, "wins": 0, "losses": 0, "draws": 0}
                
                self.player_patterns[fen][move_uci]["count"] += 1
                
                # Track outcome from player's perspective
                if result == "1-0" and player_color == chess.WHITE:
                    self.player_patterns[fen][move_uci]["wins"] += 1
                elif result == "0-1" and player_color == chess.BLACK:
                    self.player_patterns[fen][move_uci]["wins"] += 1
                elif result == "1-0" and player_color == chess.BLACK:
                    self.player_patterns[fen][move_uci]["losses"] += 1
                elif result == "0-1" and player_color == chess.WHITE:
                    self.player_patterns[fen][move_uci]["losses"] += 1
                else:
                    self.player_patterns[fen][move_uci]["draws"] += 1
            
            board.push(move)
        
        self._save_knowledge()
        self._save_player_patterns()

    def _get_player_weakness_bonus(self, fen: str) -> float:
        """Get bonus score based on how well the player performs in this position"""
        if fen not in self.player_patterns:
            return 0.0
        
        player_moves = self.player_patterns[fen]
        if not player_moves:
            return 0.0
        
        # Calculate player's win rate in this position
        total_games = sum(m.get("count", 0) for m in player_moves.values())
        if total_games < 2:  # Need at least 2 games for meaningful analysis
            return 0.0
        
        total_wins = sum(m.get("wins", 0) for m in player_moves.values())
        total_losses = sum(m.get("losses", 0) for m in player_moves.values())
        
        win_rate = total_wins / total_games if total_games > 0 else 0.5
        
        # If player has poor win rate in this position, bonus for moving there
        # Range: -100 to +100 based on how weak they are
        weakness_bonus = (0.5 - win_rate) * 200
        return weakness_bonus

    def get_move(self, board: chess.Board) -> chess.Move:
        """Get the best move for the current position"""
        # Check opening book first
        if board.fen() in self.opening_book:
            book_moves = self.opening_book[board.fen()]
            # Filter to only legal moves
            legal_book_moves = [m for m in book_moves if m in board.legal_moves]
            if legal_book_moves:
                return random.choice(legal_book_moves)  # Random choice for variety
        
        # Fall back to minimax search
        self.transposition_table.clear()
        _, move = self._minimax(board, self.max_depth, float('-inf'), float('inf'), True)
        return move if move else list(board.legal_moves)[0]

    def evaluate_board(self, board: chess.Board) -> float:
        """Comprehensive board evaluation"""
        # Terminal conditions
        if board.is_checkmate():
            return float('-inf') if board.turn else float('inf')
        
        if board.is_stalemate() or board.is_insufficient_material() or board.is_repetition():
            return 0
        
        # Material evaluation
        material_score = self._evaluate_material(board)
        
        # Positional evaluation
        position_score = self._evaluate_position(board)
        
        # Mobility evaluation
        mobility_score = self._evaluate_mobility(board)
        
        # King safety evaluation
        king_safety_score = self._evaluate_king_safety(board)
        
        # Check status bonus
        check_score = 50 if board.is_check() else 0
        
        # Player weakness/strength analysis - adjust score based on how well opponent performs in this position
        # Positive bonus if opponent typically loses here, negative if they typically win
        weakness_bonus = self._get_player_weakness_bonus(board.fen())
        
        total = material_score + position_score + mobility_score + king_safety_score + (check_score if board.turn else -check_score) + weakness_bonus
        
        return total

    def _evaluate_material(self, board: chess.Board) -> float:
        """Evaluate material balance"""
        material = 0
        for piece_type in chess.PIECE_TYPES:
            white_pieces = len(board.pieces(piece_type, chess.WHITE))
            black_pieces = len(board.pieces(piece_type, chess.BLACK))
            piece_value = self.piece_values.get(piece_type, 0)
            material += (white_pieces - black_pieces) * piece_value
        return material

    def _evaluate_position(self, board: chess.Board) -> float:
        """Evaluate positional factors using piece-square tables"""
        position = 0
        
        # Pawns
        for square in board.pieces(chess.PAWN, chess.WHITE):
            position += self.pawn_table[square]
        for square in board.pieces(chess.PAWN, chess.BLACK):
            position -= self.pawn_table[chess.square_mirror(square)]
        
        # Knights
        for square in board.pieces(chess.KNIGHT, chess.WHITE):
            position += self.knight_table[square]
        for square in board.pieces(chess.KNIGHT, chess.BLACK):
            position -= self.knight_table[chess.square_mirror(square)]
        
        # Bishops
        for square in board.pieces(chess.BISHOP, chess.WHITE):
            position += self.bishop_table[square]
        for square in board.pieces(chess.BISHOP, chess.BLACK):
            position -= self.bishop_table[chess.square_mirror(square)]
        
        # Rooks
        for square in board.pieces(chess.ROOK, chess.WHITE):
            position += self.rook_table[square]
        for square in board.pieces(chess.ROOK, chess.BLACK):
            position -= self.rook_table[chess.square_mirror(square)]
        
        # Queens
        for square in board.pieces(chess.QUEEN, chess.WHITE):
            position += self.queen_table[square]
        for square in board.pieces(chess.QUEEN, chess.BLACK):
            position -= self.queen_table[chess.square_mirror(square)]
        
        # King
        for square in board.pieces(chess.KING, chess.WHITE):
            position += self.king_table[square]
        for square in board.pieces(chess.KING, chess.BLACK):
            position -= self.king_table[chess.square_mirror(square)]
        
        return position

    def _evaluate_mobility(self, board: chess.Board) -> float:
        """Evaluate piece mobility"""
        white_moves = board.legal_moves.count()
        
        board.turn = not board.turn
        black_moves = board.legal_moves.count()
        board.turn = not board.turn
        
        return (white_moves - black_moves) * 2

    def _evaluate_king_safety(self, board: chess.Board) -> float:
        """Evaluate king safety"""
        score = 0
        
        # White king safety
        white_king_square = board.king(chess.WHITE)
        white_king_attackers = len(board.attackers(chess.BLACK, white_king_square))
        
        # Black king safety
        black_king_square = board.king(chess.BLACK)
        black_king_attackers = len(board.attackers(chess.WHITE, black_king_square))
        
        score -= white_king_attackers * 30
        score += black_king_attackers * 30
        
        return score

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                 is_maximizing: bool) -> Tuple[float, Optional[chess.Move]]:
        """Minimax with alpha-beta pruning"""
        
        fen = board.fen()
        key = (fen, depth)
        
        # Check transposition table
        if key in self.transposition_table:
            return self.transposition_table[key]
        
        # Check learned positions for guidance
        if fen in self.learned_positions:
            learned_data = self.learned_positions[fen]
            total_games = learned_data["wins"] + learned_data["losses"] + learned_data["draws"]
            if total_games > 0:
                win_rate = learned_data["wins"] / total_games
                return win_rate * 100 - 50, None  # Convert to evaluation
        
        # Terminal conditions
        if depth == 0 or board.is_game_over():
            eval_score = self.evaluate_board(board)
            self.transposition_table[key] = (eval_score, None)
            return eval_score, None
        
        legal_moves = list(board.legal_moves)
        
        # Sort moves (captures first, then checks)
        def move_order(move):
            if board.is_capture(move):
                return 0
            elif board.gives_check(move):
                return 1
            else:
                return 2
        
        legal_moves.sort(key=move_order)
        
        best_move = None
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval_score, _ = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            result = (max_eval, best_move)
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score, _ = self._minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            result = (min_eval, best_move)
        
        self.transposition_table[key] = result
        return result
