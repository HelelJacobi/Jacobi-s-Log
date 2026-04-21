# -*- coding: utf-8 -*-
"""
Chess GUI with Advanced Features
- Full chess rule support (stalemate, checkmate, en passant, pawn promotion, etc)
- Visual evaluation bar
- Learning bot that improves over time
- Adjustable difficulty (1-4)
- Player vs Bot and Bot vs Bot modes
- Modern sleek UI with cool tones
"""
import tkinter as tk
from tkinter import ttk
import chess
from ChessJBot import LearningChessBot
from typing import Optional, List

# Color palette - cool tones
COLORS = {
    "bg_dark": "#0f1419",
    "bg_light": "#1a1f2e",
    "bg_lighter": "#252b3d",
    "bg_darker": "#0d0f14",
    "accent_blue": "#4a90e2",
    "accent_cyan": "#2dd4bf",
    "text_primary": "#e0e7ff",
    "text_secondary": "#a5b4fc",
    "square_light": "#cfe9f3",
    "square_dark": "#6b8e99",
    "white_piece": "#f5f5f5",
    "black_piece": "#1a1a1a",
    "highlight_select": "#fbbf24",
    "highlight_move": "#34d399",
    "highlight_last": "#f87171",
}

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("J-Bot Chess")
        self.root.geometry("1650x1050")
        self.root.configure(bg=COLORS["bg_dark"])
        
        # Game state
        self.board = chess.Board()
        self.player_color = chess.WHITE
        self.bot_skill = 1
        self.selected_square: Optional[int] = None
        self.highlighted_moves: List[int] = []
        self.last_move: Optional[chess.Move] = None
        self.game_moves: List[chess.Move] = []
        self.bot = LearningChessBot(self.bot_skill)
        self.bot_vs_bot = False
        self.bot2_skill = 1
        self.game_in_progress = True
        self.promotion_pending = False
        self.promotion_from_square = None
        self.promotion_to_square = None
        self.status_message = "Welcome! Start a new game or continue playing."
        self.show_eval_bar = True
        
        # Bot vs Bot mode tracking
        self.bot_vs_bot_running = False
        self.white_wins = 0
        self.black_wins = 0
        self.draws = 0
        self.session_games = 0
        
        # UI Setup
        self.setup_ui()
        self.draw_board()
        self.check_game_state()

    def setup_ui(self):
        """Create UI elements with modern sleek design"""
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TScale', background=COLORS["bg_light"], troughcolor=COLORS["bg_lighter"])
        style.configure('TLabel', background=COLORS["bg_light"], foreground=COLORS["text_primary"])
        
        # Top control panel
        control_frame = tk.Frame(self.root, bg=COLORS["bg_light"], height=80)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        
        # Left side controls
        left_controls = tk.Frame(control_frame, bg=COLORS["bg_light"])
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)
        
        tk.Label(left_controls, text="Difficulty", font=("Segoe UI", 10, "bold"),
                bg=COLORS["bg_light"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(0, 10))
        
        self.difficulty_var = tk.IntVar(value=1)
        self.difficulty_scale = tk.Scale(left_controls, from_=1, to=4, orient=tk.HORIZONTAL,
                                         variable=self.difficulty_var, command=self.set_difficulty,
                                         bg=COLORS["bg_light"], fg=COLORS["accent_cyan"],
                                         troughcolor=COLORS["bg_darker"], activebackground=COLORS["accent_cyan"],
                                         highlightthickness=0, length=120, width=15)
        self.difficulty_scale.pack(side=tk.LEFT, padx=5)
        
        self.difficulty_label = tk.Label(left_controls, text="[1]", font=("Segoe UI", 11, "bold"),
                                        bg=COLORS["bg_light"], fg=COLORS["accent_cyan"], width=3)
        self.difficulty_label.pack(side=tk.LEFT, padx=(5, 15))
        
        # Eval bar toggle
        self.eval_toggle_btn = self._create_button(left_controls, "Eval: ON", self.toggle_eval_bar, 0)
        self.eval_toggle_btn.pack(side=tk.LEFT, padx=10)
        
        # Game mode selector
        tk.Label(left_controls, text="Mode", font=("Segoe UI", 10, "bold"),
                bg=COLORS["bg_light"], fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=(20, 10))
        
        self.mode_var = tk.StringVar(value="player_white")
        mode_menu = ttk.Combobox(left_controls, textvariable=self.mode_var, width=15, state="readonly",
                                 values=["Player (White)", "Player (Black)", "Bot vs Bot"])
        mode_menu.pack(side=tk.LEFT, padx=5)
        mode_menu.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())
        
        # Buttons on right
        button_frame = tk.Frame(control_frame, bg=COLORS["bg_light"])
        button_frame.pack(side=tk.RIGHT, padx=15, pady=10)
        
        self.new_game_btn = self._create_button(button_frame, "New Game", self.new_game, 0)
        self.new_game_btn.pack(side=tk.LEFT, padx=3)
        
        self.undo_btn = self._create_button(button_frame, "Undo", self.undo_move, 1)
        self.undo_btn.pack(side=tk.LEFT, padx=3)
        
        self.reset_btn = self._create_button(button_frame, "Reset", self.reset_board, 2)
        self.reset_btn.pack(side=tk.LEFT, padx=3)
        
        # Bot vs Bot control button
        self.bot_vs_bot_btn = self._create_button(button_frame, "Start Sessions", self.toggle_bot_vs_bot_mode, 3)
        self.bot_vs_bot_btn.pack(side=tk.LEFT, padx=3)
        
        # Main game area
        game_frame = tk.Frame(self.root, bg=COLORS["bg_dark"])
        game_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Chess board
        board_frame = tk.Frame(game_frame, bg=COLORS["bg_dark"])
        board_frame.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(board_frame, width=600, height=600, bg=COLORS["bg_lighter"],
                                highlightthickness=2, highlightbackground=COLORS["accent_blue"],
                                highlightcolor=COLORS["accent_cyan"])
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_square_click)
        
        # Right side - Info panels
        right_frame = tk.Frame(game_frame, bg=COLORS["bg_light"])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Top: Evaluation bar
        eval_frame = tk.Frame(right_frame, bg=COLORS["bg_light"])
        eval_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.eval_label = tk.Label(eval_frame, text="EVALUATION", font=("Segoe UI", 9, "bold"),
                bg=COLORS["bg_light"], fg=COLORS["accent_cyan"])
        self.eval_label.pack(anchor=tk.W)
        
        self.eval_canvas = tk.Canvas(eval_frame, width=35, height=300, bg=COLORS["bg_lighter"],
                                     highlightthickness=1, highlightbackground=COLORS["accent_blue"])
        self.eval_canvas.pack(pady=5)
        
        # Game info
        info_frame = tk.Frame(right_frame, bg=COLORS["bg_light"])
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(info_frame, text="GAME INFO", font=("Segoe UI", 9, "bold"),
                bg=COLORS["bg_light"], fg=COLORS["accent_cyan"]).pack(anchor=tk.W)
        
        self.info_text = tk.Text(info_frame, width=28, height=10, font=("Consolas", 8),
                                bg=COLORS["bg_darker"], fg=COLORS["text_primary"],
                                insertbackground=COLORS["accent_cyan"], relief=tk.FLAT, borderwidth=1)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.info_text.config(state=tk.DISABLED)
        
        # Move history
        moves_frame = tk.Frame(right_frame, bg=COLORS["bg_light"])
        moves_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(moves_frame, text="MOVES", font=("Segoe UI", 9, "bold"),
                bg=COLORS["bg_light"], fg=COLORS["accent_cyan"]).pack(anchor=tk.W)
        
        self.move_list = tk.Text(moves_frame, width=28, height=8, font=("Consolas", 8),
                                bg=COLORS["bg_darker"], fg=COLORS["text_primary"],
                                insertbackground=COLORS["accent_cyan"], relief=tk.FLAT, borderwidth=1)
        self.move_list.pack(fill=tk.BOTH, expand=True, pady=5)
        self.move_list.config(state=tk.DISABLED)
        
        # Status bar at bottom
        status_frame = tk.Frame(self.root, bg=COLORS["bg_lighter"], height=40)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        
        self.status_label = tk.Label(status_frame, text=self.status_message,
                                     font=("Segoe UI", 9), bg=COLORS["bg_lighter"],
                                     fg=COLORS["text_secondary"], justify=tk.LEFT)
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10, anchor=tk.W)
        
        self.update_info()
    
    def _create_button(self, parent, text, command, index):
        """Create a styled button"""
        btn = tk.Button(parent, text=text, command=command, font=("Segoe UI", 9, "bold"),
                       bg=COLORS["accent_blue"], fg=COLORS["text_primary"],
                       activebackground=COLORS["accent_cyan"], activeforeground=COLORS["bg_dark"],
                       relief=tk.FLAT, padx=12, pady=6, cursor="hand2", borderwidth=0)
        return btn
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_message = message
        self.status_label.config(text=message)

    def set_difficulty(self, value):
        """Set bot difficulty"""
        self.bot_skill = int(value)
        self.difficulty_label.config(text=f"[{self.bot_skill}]")
        self.bot = LearningChessBot(self.bot_skill)
        self.update_status(f"Difficulty set to {self.bot_skill}")
    
    def toggle_eval_bar(self):
        """Toggle evaluation bar visibility"""
        self.show_eval_bar = not self.show_eval_bar
        status = "ON" if self.show_eval_bar else "OFF"
        self.eval_toggle_btn.config(text=f"Eval: {status}")
        self.draw_board()
    
    def toggle_bot_vs_bot_mode(self):
        """Toggle bot vs bot continuous play"""
        if not self.bot_vs_bot:
            self.update_status("Switch to Bot vs Bot mode first!")
            return
        
        self.bot_vs_bot_running = not self.bot_vs_bot_running
        if self.bot_vs_bot_running:
            self.bot_vs_bot_btn.config(text="Stop Sessions")
            self.reset_bot_vs_bot_stats()
            self.reset_board()
            self.update_status("Bot vs Bot continuous play started!")
            self.next_bot_game()
        else:
            self.bot_vs_bot_btn.config(text="Start Sessions")
            self.update_status(f"Bot vs Bot stopped - W:{self.white_wins} B:{self.black_wins} D:{self.draws}")
    
    def reset_bot_vs_bot_stats(self):
        """Reset bot vs bot statistics"""
        self.white_wins = 0
        self.black_wins = 0
        self.draws = 0
        self.session_games = 0
    
    def next_bot_game(self):
        """Start the next bot vs bot game"""
        if not self.bot_vs_bot_running:
            return
        
        self.reset_board()
        self.check_game_state()
    
    def on_mode_change(self):
        """Handle game mode change"""
        mode = self.mode_var.get()
        
        if mode == "Player (White)":
            self.bot_vs_bot = False
            self.bot_vs_bot_running = False
            self.player_color = chess.WHITE
            self.update_status("Mode: You play as White")
        elif mode == "Player (Black)":
            self.bot_vs_bot = False
            self.bot_vs_bot_running = False
            self.player_color = chess.BLACK
            self.update_status("Mode: You play as Black")
        elif mode == "Bot vs Bot":
            self.bot_vs_bot = True
            self.bot_vs_bot_running = False
            self.update_status("Mode: Bot vs Bot - Click 'Start Sessions' to begin")
        
        self.reset_board()

    def new_game(self):
        """Start a new game"""
        self.reset_board()
    
    def show_bot2_difficulty_dialog(self):
        """Show integrated dialog for bot2 difficulty (unused in continuous mode)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Bot 2 Difficulty")
        dialog.geometry("300x120")
        dialog.configure(bg=COLORS["bg_light"])
        dialog.grab_set()
        
        tk.Label(dialog, text="Bot 2 Difficulty (1-4):", font=("Segoe UI", 10),
                bg=COLORS["bg_light"], fg=COLORS["text_primary"]).pack(pady=10)
        
        var = tk.IntVar(value=1)
        scale = tk.Scale(dialog, from_=1, to=4, orient=tk.HORIZONTAL, variable=var,
                        bg=COLORS["bg_lighter"], fg=COLORS["accent_cyan"])
        scale.pack(padx=20, pady=5, fill=tk.X)
        
        def confirm():
            self.bot2_skill = var.get()
            dialog.destroy()
        
        btn = tk.Button(dialog, text="OK", command=confirm, font=("Segoe UI", 10, "bold"),
                       bg=COLORS["accent_blue"], fg=COLORS["text_primary"],
                       relief=tk.FLAT, padx=20, pady=5)
        btn.pack(pady=10)
    
    def reset_board(self):
        """Reset the board for a new game"""
        self.board = chess.Board()
        self.selected_square = None
        self.highlighted_moves = []
        self.last_move = None
        self.game_moves = []
        self.game_in_progress = True
        self.promotion_pending = False
        self.draw_board()
        self.update_info()
        self.update_status("Game started! Make your move.")
        self.check_game_state()

    def undo_move(self):
        """Undo the last move"""
        if len(self.game_moves) >= 2:
            self.board.pop()
            self.game_moves.pop()
            self.board.pop()
            self.game_moves.pop()
            self.last_move = self.game_moves[-1] if self.game_moves else None
            self.update_status("Undid last two moves (bot + player)")
            self.draw_board()
            self.update_info()
            self.game_in_progress = True
        elif len(self.game_moves) == 1 and not self.bot_vs_bot:
            self.board.pop()
            self.game_moves.pop()
            self.last_move = None
            self.update_status("Undid your move")
            self.draw_board()
            self.update_info()
            self.game_in_progress = True
        else:
            self.update_status("No moves to undo")

    def draw_board(self):
        """Draw the chess board"""
        self.canvas.delete("all")
        
        square_size = 75
        light_color = COLORS["square_light"]
        dark_color = COLORS["square_dark"]
        
        for rank in range(8):
            for file in range(8):
                # Flip board if player is Black
                chess_file = 7 - file if self.player_color == chess.BLACK else file
                chess_rank = rank if self.player_color == chess.BLACK else 7 - rank
                square = chess.square(chess_file, chess_rank)
                x1, y1 = file * square_size, rank * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                
                # Determine square color
                color = light_color if (file + rank) % 2 == 0 else dark_color
                
                # Highlight special squares
                if self.selected_square == square:
                    color = COLORS["highlight_select"]
                elif square in self.highlighted_moves:
                    color = COLORS["highlight_move"]
                elif self.last_move and square in [self.last_move.from_square, self.last_move.to_square]:
                    color = COLORS["highlight_last"]
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORS["bg_darker"], width=1)
                
                # Draw piece
                piece = self.board.piece_at(square)
                if piece:
                    symbol = self.get_piece_symbol(piece)
                    self.canvas.create_text(x1 + square_size//2, y1 + square_size//2, 
                                           text=symbol, font=("Arial", 36, "bold"))
                
                # Draw coordinates
                if file == 0:
                    self.canvas.create_text(x1 + 2, y1 + 2, text=str(8 - rank), 
                                           font=("Arial", 8), anchor="nw", fill=COLORS["text_secondary"])
                if rank == 7:
                    self.canvas.create_text(x2 - 2, y2 - 2, text=chr(97 + file), 
                                           font=("Arial", 8), anchor="se", fill=COLORS["text_secondary"])
        
        self.draw_evaluation_bar()
        self.update_move_list()

    def draw_evaluation_bar(self):
        """Draw the evaluation bar or win graph depending on mode"""
        self.eval_canvas.delete("all")
        
        # In bot vs bot mode, show win statistics graph
        if self.bot_vs_bot:
            self.eval_label.config(text="SESSION STATS")
            self.draw_win_graph()
        else:
            self.eval_label.config(text="EVALUATION")
            # Standard evaluation bar
            if not self.show_eval_bar:
                return
            
            try:
                score = self.bot.evaluate_board(self.board)
                # Normalize score to -1 to 1 range
                normalized = max(min(score / 500, 1), -1)
                
                # Draw background
                self.eval_canvas.create_rectangle(0, 0, 35, 300, fill=COLORS["bg_darker"], outline=COLORS["accent_blue"])
                
                # Calculate heights
                center = 150
                white_height = int((1 - normalized) * center)
                black_height = int((1 + normalized) * center)
                
                # Draw eval bar
                if white_height > 0:
                    self.eval_canvas.create_rectangle(0, 0, 35, white_height, 
                                                     fill=COLORS["square_light"], outline="")
                if black_height > 0:
                    self.eval_canvas.create_rectangle(0, 300 - black_height, 35, 300, 
                                                     fill=COLORS["square_dark"], outline="")
                
                # Draw center line
                self.eval_canvas.create_line(0, center, 35, center, fill=COLORS["accent_cyan"], width=2)
                
                # Draw score text
                score_text = f"{score:.0f}"
                self.eval_canvas.create_text(17, 10, text=score_text, fill=COLORS["accent_cyan"], 
                                            font=("Arial", 9, "bold"))
            except:
                self.eval_canvas.create_rectangle(0, 0, 35, 300, fill=COLORS["bg_darker"], outline=COLORS["accent_blue"])

    def draw_win_graph(self):
        """Draw win statistics graph for bot vs bot mode"""
        self.eval_canvas.create_rectangle(0, 0, 35, 300, fill=COLORS["bg_darker"], outline=COLORS["accent_blue"])
        
        total = self.white_wins + self.black_wins + self.draws
        if total == 0:
            return
        
        # Draw proportional bars for wins
        white_ratio = self.white_wins / total if total > 0 else 0
        black_ratio = self.black_wins / total if total > 0 else 0
        draw_ratio = self.draws / total if total > 0 else 0
        
        white_height = int(white_ratio * 300)
        black_height = int(black_ratio * 300)
        draw_height = int(draw_ratio * 300)
        
        # Draw stacked bars
        y_offset = 0
        if white_height > 0:
            self.eval_canvas.create_rectangle(0, y_offset, 35, y_offset + white_height, 
                                             fill=COLORS["square_light"], outline="")
            self.eval_canvas.create_text(17, y_offset + white_height // 2, 
                                        text=f"{self.white_wins}", fill=COLORS["accent_cyan"], 
                                        font=("Arial", 8, "bold"))
            y_offset += white_height
        
        if draw_height > 0:
            self.eval_canvas.create_rectangle(0, y_offset, 35, y_offset + draw_height, 
                                             fill=COLORS["accent_cyan"], outline="")
            self.eval_canvas.create_text(17, y_offset + draw_height // 2, 
                                        text=f"{self.draws}", fill=COLORS["bg_darker"], 
                                        font=("Arial", 8, "bold"))
            y_offset += draw_height
        
        if black_height > 0:
            self.eval_canvas.create_rectangle(0, y_offset, 35, y_offset + black_height, 
                                             fill=COLORS["square_dark"], outline="")
            self.eval_canvas.create_text(17, y_offset + black_height // 2, 
                                        text=f"{self.black_wins}", fill=COLORS["accent_cyan"], 
                                        font=("Arial", 8, "bold"))

    def update_move_list(self):
        """Update the displayed move list"""
        self.move_list.config(state=tk.NORMAL)
        self.move_list.delete(1.0, tk.END)
        
        temp_board = chess.Board()
        move_num = 1
        
        for i, move in enumerate(self.game_moves):
            san_move = temp_board.san(move)
            temp_board.push(move)
            
            if i % 2 == 0:
                self.move_list.insert(tk.END, f"{move_num}. {san_move} ")
                move_num += 1
            else:
                self.move_list.insert(tk.END, f"{san_move}\n")
        
        self.move_list.config(state=tk.DISABLED)

    def update_info(self):
        """Update game information display"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        # Determine mode display
        if self.bot_vs_bot:
            mode_str = f"Bot {self.bot_skill} vs Bot {self.bot2_skill}"
        else:
            player_color = "White" if self.player_color == chess.WHITE else "Black"
            mode_str = f"Player ({player_color}) vs Bot {self.bot_skill}"
        
        info = f"Turn: {('White' if self.board.turn else 'Black'):6} │ Move: {self.board.fullmove_number}\n"
        info += f"Mode: {mode_str}\n"
        info += f"Legal Moves: {self.board.legal_moves.count():3} │ HM Clock: {self.board.halfmove_clock}\n"
        info += "─" * 26 + "\n"
        
        # Game status
        if self.board.is_checkmate():
            winner = "White" if not self.board.turn else "Black"
            info += f"✓ CHECKMATE!\n{winner} wins!"
        elif self.board.is_stalemate():
            info += "═ STALEMATE\nGame is drawn"
        elif self.board.is_insufficient_material():
            info += "═ INSUFFICIENT\nMaterial (Draw)"
        elif self.board.is_repetition():
            info += "═ REPETITION\nGame is drawn"
        elif self.board.halfmove_clock >= 100:
            info += "═ 50-MOVE RULE\nGame is drawn"
        elif self.board.is_check():
            info += "⚠ CHECK!"
        else:
            info += "● Game ongoing"
        
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)

    def on_square_click(self, event):
        """Handle square click"""
        if not self.game_in_progress:
            return
        
        # If promotion pending, ignore board clicks
        if self.promotion_pending:
            return
        
        # If bot's turn, ignore
        if self.board.turn != self.player_color and not self.bot_vs_bot:
            return
        
        # If bot vs bot, ignore
        if self.bot_vs_bot:
            return
        
        square = chess.square(
            7 - (event.x // 75) if self.player_color == chess.BLACK else event.x // 75,
            event.y // 75 if self.player_color == chess.BLACK else 7 - (event.y // 75)
        )
        
        if self.selected_square is None:
            # Select piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.highlighted_moves = [m.to_square for m in self.board.legal_moves 
                                         if m.from_square == square]
        else:
            # Try to move
            if square == self.selected_square:
                # Deselect
                self.selected_square = None
                self.highlighted_moves = []
            else:
                # Attempt move
                move = chess.Move(self.selected_square, square)
                
                # Check for pawn promotion
                piece_at_source = self.board.piece_at(self.selected_square)
                if (piece_at_source and piece_at_source.piece_type == chess.PAWN and
                    square in [chess.square(f, r) for f in range(8) for r in (0, 7)]):
                    # Show promotion dropdown
                    self.show_promotion_dropdown(self.selected_square, square)
                    self.selected_square = None
                    self.highlighted_moves = []
                    self.draw_board()
                    return
                
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.game_moves.append(move)
                    self.last_move = move
                    self.selected_square = None
                    self.highlighted_moves = []
                    self.draw_board()
                    self.update_info()
                    self.check_game_state()
                else:
                    # Invalid move, select new piece
                    piece = self.board.piece_at(square)
                    if piece and piece.color == self.board.turn:
                        self.selected_square = square
                        self.highlighted_moves = [m.to_square for m in self.board.legal_moves 
                                                 if m.from_square == square]
                    else:
                        self.selected_square = None
                        self.highlighted_moves = []
        
        self.draw_board()
    
    def show_promotion_dropdown(self, from_sq, to_sq):
        """Show promotion piece selector"""
        self.promotion_pending = True
        self.promotion_from_square = from_sq
        self.promotion_to_square = to_sq
        
        # Create promotion menu frame
        menu_frame = tk.Frame(self.root, bg=COLORS["bg_light"], relief=tk.RAISED, bd=2)
        menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(menu_frame, text="Choose Promotion Piece:", font=("Segoe UI", 11, "bold"),
                bg=COLORS["bg_light"], fg=COLORS["text_primary"]).pack(pady=10, padx=10)
        
        pieces = [("Queen", chess.QUEEN, "♕"), ("Rook", chess.ROOK, "♖"), 
                 ("Bishop", chess.BISHOP, "♗"), ("Knight", chess.KNIGHT, "♘")]
        
        for name, piece_type, symbol in pieces:
            btn = tk.Button(menu_frame, text=f"{symbol} {name}", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["accent_blue"], fg=COLORS["text_primary"],
                           activebackground=COLORS["accent_cyan"], activeforeground=COLORS["bg_dark"],
                           relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
                           command=lambda p=piece_type, f=menu_frame: self.make_promotion_move(p, f))
            btn.pack(pady=3, padx=10, fill=tk.X)
        
        self.root.update()
    
    def make_promotion_move(self, promotion_piece, menu_frame):
        """Execute promotion move"""
        move = chess.Move(self.promotion_from_square, self.promotion_to_square, promotion=promotion_piece)
        
        if move in self.board.legal_moves:
            self.board.push(move)
            self.game_moves.append(move)
            self.last_move = move
            self.update_status(f"Promoted to {['', 'P', 'N', 'B', 'R', 'Q', 'K'][promotion_piece]}")
        
        menu_frame.destroy()
        self.promotion_pending = False
        self.promotion_from_square = None
        self.promotion_to_square = None
        self.draw_board()
        self.update_info()
        self.check_game_state()

    def get_piece_symbol(self, piece: chess.Piece) -> str:
        """Get unicode symbol for piece"""
        symbols = {
            chess.PAWN: ('♙', '♟'),
            chess.KNIGHT: ('♘', '♞'),
            chess.BISHOP: ('♗', '♝'),
            chess.ROOK: ('♖', '♜'),
            chess.QUEEN: ('♕', '♛'),
            chess.KING: ('♔', '♚'),
        }
        white_sym, black_sym = symbols[piece.piece_type]
        return white_sym if piece.color == chess.WHITE else black_sym

    def check_game_state(self):
        """Check game state and handle bot moves"""
        self.draw_board()
        self.update_info()
        
        if not self.game_in_progress:
            return
        
        # Check for game end
        if self.board.is_game_over():
            result = self.board.result()
            outcome = self.board.outcome()
            
            # Learn from game
            self.bot.learn_from_game(self.game_moves, result)
            
            # Track wins in bot vs bot mode
            if self.bot_vs_bot:
                if result == "1-0":
                    self.white_wins += 1
                elif result == "0-1":
                    self.black_wins += 1
                else:
                    self.draws += 1
                self.session_games += 1
                
                # Continue to next game if running
                if self.bot_vs_bot_running:
                    self.root.after(1000, self.next_bot_game)
                    return
            
            # Determine end message
            if outcome:
                reason = outcome.termination.name.replace('_', ' ').title()
                status_msg = f"Game Over! Result: {result} ({reason})"
            else:
                status_msg = f"Game Over! Result: {result}"
            
            self.update_status(status_msg)
            self.game_in_progress = False
            self.draw_board()
            return
        
        # Handle bot moves
        if self.bot_vs_bot:
            if self.board.turn == chess.WHITE:
                bot = self.bot
            else:
                bot = LearningChessBot(self.bot2_skill)
            
            self.root.after(500, lambda: self.make_bot_move(bot))
        elif self.board.turn != self.player_color:
            player_turn = "White" if self.player_color == chess.WHITE else "Black"
            self.update_status(f"Bot is thinking... ({player_turn} to move)")
            self.root.after(500, lambda: self.make_bot_move(self.bot))
        else:
            player_turn = "White" if self.player_color == chess.WHITE else "Black"
            opponent = "Black" if self.player_color == chess.WHITE else "White"
            self.update_status(f"Your turn ({player_turn}) - Click a piece to move")
    
    def make_bot_move(self, bot: LearningChessBot):
        """Make a bot move"""
        if not self.game_in_progress or self.board.is_game_over():
            return
        
        move = bot.get_move(self.board)
        if move:
            move_san = self.board.san(move)
            self.board.push(move)
            self.game_moves.append(move)
            self.last_move = move
            self.update_status(f"Bot played: {move_san}")
        
        self.check_game_state()

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
