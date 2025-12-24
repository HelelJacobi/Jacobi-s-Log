import tkinter as tk
from tkinter import messagebox, simpledialog
import chess
import chess.polyglot
from collections import defaultdict

position_counter = defaultdict(int)

# Evaluation parameters
piece_square_tables = {
    chess.PAWN: [0, 5, 5, 0, 5, 10, 50, 0] * 8,
    chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50] * 8,
    chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20] * 8,
    chess.ROOK: [0, 0, 0, 5, 5, 0, 0, 0] * 8,
    chess.QUEEN: [-20, -10, -10, -5, -5, -10, -10, -20] * 8,
    chess.KING: [20, 30, 10, 0, 0, 10, 30, 20] * 8,
}

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 10000,
}

unicode_pieces = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}

transposition_table = {}

def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    value = 0
    for piece_type in piece_values:
        for square in board.pieces(piece_type, chess.WHITE):
            value += piece_values[piece_type] + piece_square_tables[piece_type][square]
        for square in board.pieces(piece_type, chess.BLACK):
            mirrored = chess.square_mirror(square)
            value -= piece_values[piece_type] + piece_square_tables[piece_type][mirrored]
    return value

def quiescence(board, alpha, beta, is_max):
    stand_pat = evaluate_board(board)
    if is_max:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = quiescence(board, alpha, beta, not is_max)
            board.pop()
            if is_max:
                alpha = max(alpha, score)
            else:
                beta = min(beta, score)
            if alpha >= beta:
                break
    return alpha if is_max else beta

def minimax(board, depth, alpha, beta, is_max):
    key = (board.fen(), depth)
    if key in transposition_table:
        return transposition_table[key]

    if board.is_game_over() or depth == 0:
        eval = quiescence(board, alpha, beta, is_max)
        # Penalize repeated positions
        if position_counter[board.fen()] > 0:
            eval -= 2000  # Large penalty for repetition
        result = eval, None
        transposition_table[key] = result
        return result

    best_move = None
    moves = sorted(board.legal_moves, key=lambda m: board.is_capture(m), reverse=True)

    if is_max:
        max_eval = float('-inf')
        for move in moves:
            board.push(move)
            position_counter[board.fen()] += 1

            eval, _ = minimax(board, depth - 1, alpha, beta, False)

            position_counter[board.fen()] -= 1
            board.pop()

            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        result = max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            board.push(move)
            position_counter[board.fen()] += 1

            eval, _ = minimax(board, depth - 1, alpha, beta, True)

            position_counter[board.fen()] -= 1
            board.pop()

            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        result = min_eval, best_move

    transposition_table[key] = result
    return result


class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JBot")

        self.board = chess.Board()
        self.player_color = chess.WHITE
        self.selected_square = None
        self.highlighted_moves = []
        self.last_move = None

        self.elo = 3
        self.bot_vs_bot_mode = False
        self.bot1_elo = 2
        self.bot2_elo = 2

        self.create_widgets()
        self.draw_board()
        self.check_bot_turn()

    def create_widgets(self):
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP)

        tk.Label(top, text="Play as:").pack(side=tk.LEFT)
        self.color_choice = tk.StringVar(value="White")
        tk.OptionMenu(top, self.color_choice, "White", "Black", command=self.set_color).pack(side=tk.LEFT)

        tk.Button(top, text="Bot vs Bot", command=self.toggle_bot_vs_bot).pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, width=480, height=480)
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.on_click)

        self.eval_canvas = tk.Canvas(self.root, width=30, height=480, bg="white")
        self.eval_canvas.pack(side=tk.LEFT, padx=5)

        self.move_list = tk.Text(self.root, width=35, height=30)
        self.move_list.pack(side=tk.RIGHT, padx=10)

    def toggle_bot_vs_bot(self):
        self.bot_vs_bot_mode = True
        self.bot1_elo = int(simpledialog.askstring("Bot 1 ELO (White)", "Enter ELO depth for bot 1 (1-4):", initialvalue="1"))
        self.bot2_elo = int(simpledialog.askstring("Bot 2 ELO (Black)", "Enter ELO depth for bot 2 (1-4):", initialvalue="1"))
        self.board.reset()
        self.last_move = None
        self.draw_board()

    def set_color(self, color):
        self.player_color = chess.WHITE if color == "White" else chess.BLACK
        self.elo = int(simpledialog.askstring("ELO Difficulty", "Enter bot ELO (1-4):", initialvalue="1"))
        self.board.reset()
        self.selected_square = None
        self.highlighted_moves = []
        self.last_move = None
        self.bot_vs_bot_mode = False
        self.draw_board()
        self.check_bot_turn()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#EEEED2", "#769656"]

        for rank in range(8):
            for file in range(8):
                x1, y1 = file * 60, rank * 60
                square = chess.square(file, 7 - rank)
                color = colors[(file + rank) % 2]

                if self.selected_square == square:
                    color = "#F6F669"
                elif square in self.highlighted_moves:
                    color = "#AACA61"
                elif self.last_move and square in [self.last_move.from_square, self.last_move.to_square]:
                    color = "#FF6666"

                self.canvas.create_rectangle(x1, y1, x1+60, y1+60, fill=color, outline="black")
                piece = self.board.piece_at(square)
                if piece:
                    symbol = unicode_pieces[piece.symbol()]
                    self.canvas.create_text(x1 + 30, y1 + 30, text=symbol, font=("Arial", 32))

        self.update_move_list()
        self.draw_eval_bar()

    def draw_eval_bar(self):
        self.eval_canvas.delete("all")
        score = evaluate_board(self.board)
        score = max(min(score / 1000.0, 1), -1)
        white_height = int((1 - score) * 240)
        black_height = 480 - white_height
        self.eval_canvas.create_rectangle(0, 0, 30, white_height, fill="white", outline="")
        self.eval_canvas.create_rectangle(0, white_height, 30, 480, fill="black", outline="")

    def update_move_list(self):
        self.move_list.delete(1.0, tk.END)
        temp_board = chess.Board()
        moves = list(self.board.move_stack)
        for i in range(0, len(moves), 2):
            white = temp_board.san(moves[i]) if i < len(moves) else ""
            temp_board.push(moves[i])
            black = ""
            if i + 1 < len(moves):
                black = temp_board.san(moves[i+1])
                temp_board.push(moves[i+1])
            self.move_list.insert(tk.END, f"{(i//2)+1}. {white} {black}\n")

    def on_click(self, event):
        if self.board.turn != self.player_color or self.board.is_game_over() or self.bot_vs_bot_mode:
            return

        square = chess.square(event.x // 60, 7 - event.y // 60)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self.highlighted_moves = [m.to_square for m in self.board.legal_moves if m.from_square == square]
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                if chess.square_rank(square) in [0, 7] and self.board.piece_at(self.selected_square).piece_type == chess.PAWN:
                    choice = simpledialog.askstring("Promotion", "Promote to (q, r, b, n):", initialvalue="q")
                    promote_map = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
                    move.promotion = promote_map.get(choice.lower(), chess.QUEEN)
                self.board.push(move)
                self.last_move = move
                self.selected_square = None
                self.highlighted_moves = []
                self.draw_board()
                self.check_bot_turn()
                return
            else:
                self.selected_square = None
                self.highlighted_moves = []
        self.draw_board()

    def bot_move(self, elo):
        if self.board.is_game_over():
            self.show_end_screen()
            return
        _, move = minimax(self.board, elo, float('-inf'), float('inf'), self.board.turn == chess.WHITE)
        if move:
            self.board.push(move)
            self.last_move = move
            self.draw_board()
            if self.board.is_game_over():
                self.show_end_screen()

    def show_end_screen(self):
        outcome = self.board.outcome()
        if outcome:
            result = self.board.result()
            reason = outcome.termination.name.replace("_", " ").title()
            messagebox.showinfo("Game Over", f"Result: {result}\nReason: {reason}")

    def check_bot_turn(self):
        if self.bot_vs_bot_mode:
            if not self.board.is_game_over():
                elo = self.bot1_elo if self.board.turn == chess.WHITE else self.bot2_elo
                self.bot_move(elo)
        elif self.board.turn != self.player_color and not self.board.is_game_over():
            self.bot_move(self.elo)
        self.root.after(250, self.check_bot_turn)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
