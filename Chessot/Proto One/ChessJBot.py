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

    def _is_endgame(self, board: chess.Board) -> bool:
        """Check if we're in an endgame (fewer than 8 pieces on board)"""
        total_pieces = len(board.pieces(chess.PAWN, chess.WHITE)) + len(board.pieces(chess.PAWN, chess.BLACK))
        total_pieces += len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.KNIGHT, chess.BLACK))
        total_pieces += len(board.pieces(chess.BISHOP, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.BLACK))
        total_pieces += len(board.pieces(chess.ROOK, chess.WHITE)) + len(board.pieces(chess.ROOK, chess.BLACK))
        total_pieces += len(board.pieces(chess.QUEEN, chess.WHITE)) + len(board.pieces(chess.QUEEN, chess.BLACK))
        return total_pieces < 8

    def _evaluate_endgame(self, board: chess.Board) -> float:
        """Evaluate endgame with strategic precision"""
        # Endgame: drive opponent king to edge, centralize own king
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        
        # Material is critical in endgame
        material = self._evaluate_material(board)
        
        # If winning material, drive enemy king to edge
        if material > 200:  # Winning position
            # Distance from center favors pushing enemy king away
            black_king_edge_distance = min(
                chess.square_file(black_king),
                7 - chess.square_file(black_king),
                chess.square_rank(black_king),
                7 - chess.square_rank(black_king)
            )
            # Centralize own king
            white_king_centralization = 7 - min(
                abs(3 - chess.square_file(white_king)),
                abs(3 - chess.square_rank(white_king))
            )
            endgame_score = (black_king_edge_distance * 50) + (white_king_centralization * 30)
        elif material < -200:  # Losing position
            # Opposite strategy: keep opponent king in center, centralize own king
            white_king_edge_distance = min(
                chess.square_file(white_king),
                7 - chess.square_file(white_king),
                chess.square_rank(white_king),
                7 - chess.square_rank(white_king)
            )
            black_king_centralization = 7 - min(
                abs(3 - chess.square_file(black_king)),
                abs(3 - chess.square_rank(black_king))
            )
            endgame_score = (white_king_edge_distance * 50) + (black_king_centralization * 30)
        else:
            endgame_score = 0
        
        return material + endgame_score + self._evaluate_position(board) + self._evaluate_king_safety(board)

    def _detect_hanging_pieces(self, board, color):
        hanging = {}

        for piece_type in chess.PIECE_TYPES:
            if piece_type == chess.KING:
                continue

            for square in board.pieces(piece_type, color):
                attackers = len(board.attackers(not color, square))
                defenders = len(board.attackers(color, square))

                if attackers > 0 and defenders == 0:
                    hanging[square] = self.piece_values[piece_type]

        return hanging

    def _evaluate_tactics(self, board):
        score = 0

        # Black hanging pieces = good for White
        black_hanging = self._detect_hanging_pieces(board, chess.BLACK)
        for _, value in black_hanging.items():
            score += value * 0.7

        # White hanging pieces = bad for White
        white_hanging = self._detect_hanging_pieces(board, chess.WHITE)
        for _, value in white_hanging.items():
            score -= value * 0.7

        return score

    def _detect_castled_king(self, board: chess.Board, color: int) -> Optional[str]:
        """Detect if king has castled and where (kingside/queenside)"""
        king = board.king(color)
        
        if color == chess.WHITE:
            if king == chess.G1:
                return "kingside"  # Castled kingside (g-file)
            elif king == chess.C1:
                return "queenside"  # Castled queenside (c-file)
        else:
            if king == chess.G8:
                return "kingside"
            elif king == chess.C8:
                return "queenside"
        
        return None

    def _evaluate_pawn_strategy(self, board: chess.Board) -> float:
        """Evaluate pawn attacks near opponent's castled king"""
        score = 0
        opponent_color = not board.turn
        opponent_castled = self._detect_castled_king(board, opponent_color)
        
        if opponent_castled:
            our_pawns = board.pieces(chess.PAWN, board.turn)
            
            if opponent_castled == "kingside":
                # Attack f, g, h files near king
                attack_files = [5, 6, 7]  # f, g, h files
                for pawn in our_pawns:
                    if chess.square_file(pawn) in attack_files:
                        rank = chess.square_rank(pawn)
                        # Reward advanced pawns attacking kingside
                        if board.turn == chess.WHITE and rank >= 4:
                            score += (rank - 2) * 10
                        elif board.turn == chess.BLACK and rank <= 3:
                            score += (5 - rank) * 10
            
            elif opponent_castled == "queenside":
                # Attack a, b, c files near king
                attack_files = [0, 1, 2]  # a, b, c files
                for pawn in our_pawns:
                    if chess.square_file(pawn) in attack_files:
                        rank = chess.square_rank(pawn)
                        if board.turn == chess.WHITE and rank >= 4:
                            score += (rank - 2) * 10
                        elif board.turn == chess.BLACK and rank <= 3:
                            score += (5 - rank) * 10
        
        return score

    def get_move(self, board: chess.Board) -> chess.Move:
        """Get the best move for the current position"""
        
        if board.fen() in self.opening_book:
            book_moves = self.opening_book[board.fen()]
            legal_book_moves = [m for m in book_moves if m in board.legal_moves]
            if legal_book_moves:
                return random.choice(legal_book_moves)

        self.transposition_table.clear()

        is_maximizing = (board.turn == chess.WHITE)

        _, move = self._minimax(
            board,
            self.max_depth,
            float('-inf'),
            float('inf'),
            is_maximizing
        )

        return move if move else list(board.legal_moves)[0]

    def evaluate_board(self, board):
        if board.is_checkmate():
            return -999999 if board.turn == chess.WHITE else 999999

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        # repetition = mild penalty
        repetition_penalty = 0
        if board.is_repetition(2):
            repetition_penalty = -40 if board.turn == chess.WHITE else 40

        if board.can_claim_threefold_repetition():
            repetition_penalty = -80 if board.turn == chess.WHITE else 80

        total = (
            self._evaluate_material(board)
            + self._evaluate_position(board)
            + self._evaluate_mobility(board)
            + self._evaluate_king_safety(board)
            + self._evaluate_tactics(board)
        )

        return total + repetition_penalty

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
        copy = board.copy()
        copy.turn = chess.WHITE
        white_moves = copy.legal_moves.count()

        copy.turn = chess.BLACK
        black_moves = copy.legal_moves.count()
        
        return (white_moves - black_moves) * 2

    def _evaluate_king_safety(self, board):
        score = 0

        white_sq = board.king(chess.WHITE)
        black_sq = board.king(chess.BLACK)

        white_file = chess.square_file(white_sq)
        white_rank = chess.square_rank(white_sq)

        black_file = chess.square_file(black_sq)
        black_rank = chess.square_rank(black_sq)

        white_center = min(
            abs(3 - white_file),
            abs(4 - white_file),
            abs(3 - white_rank),
            abs(4 - white_rank)
        )

        black_center = min(
            abs(3 - black_file),
            abs(4 - black_file),
            abs(3 - black_rank),
            abs(4 - black_rank)
        )

        if not self._is_endgame(board):
            white_safe = white_rank == 0 and white_file in [1, 6]
            black_safe = black_rank == 7 and black_file in [1, 6]

            score -= white_center * 15
            score += black_center * 15

            if white_safe:
                score += 40
            if black_safe:
                score -= 40

        white_attackers = len(board.attackers(chess.BLACK, white_sq))
        black_attackers = len(board.attackers(chess.WHITE, black_sq))

        score -= white_attackers * 40
        score += black_attackers * 40

        return score

    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                 is_maximizing: bool) -> Tuple[float, Optional[chess.Move]]:
        """Minimax with alpha-beta pruning"""
        
        fen = board.board_fen()
        key = (fen, depth)
        
        # Check transposition table
        if key in self.transposition_table:
            return self.transposition_table[key]
        
        # Check learned positions for guidance
        learn_bonus = 0
        if fen in self.learned_positions:
            data = self.learned_positions[fen]
            total = data["wins"] + data["losses"] + data["draws"]

            if total >= 5:
                learn_bonus = ((data["wins"] - data["losses"]) / total) * 20
        
        
        # Terminal conditions
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board) + learn_bonus, None
        
        legal_moves = list(board.legal_moves)
        
        # Advanced move ordering: prioritize good moves, penalize bad ones
        def move_order(move):
            score = 0

            if board.is_capture(move):
                captured = board.piece_at(move.to_square)
                if captured:
                    score -= self.piece_values[captured.piece_type]

            if board.gives_check(move):
                score -= 50

            return score
        
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
