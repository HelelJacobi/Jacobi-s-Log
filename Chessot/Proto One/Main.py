# -*- coding: utf-8 -*-
"""
Command-line Chess Game with Learning Bot
Supports: Human vs Bot and Bot vs Bot modes
Full chess rules: stalemate, checkmate, en passant, pawn promotion, etc.
"""
import chess
from ChessBot import LearningChessBot

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.game_moves = []
        self.human_color = None
        self.bot_skill = 2
        self.bot = LearningChessBot(self.bot_skill)
        
    def display_board(self):
        """Display the chess board"""
        print("\n" + self.board.unicode())
        print(f"\nFEN: {self.board.fen()}\n")
    
    def show_game_status(self):
        """Show current game status"""
        if self.board.is_checkmate():
            winner = "White" if not self.board.turn else "Black"
            print(f"♔ CHECKMATE! {winner} wins! ♔\n")
            return True
        elif self.board.is_stalemate():
            print("♕ STALEMATE - Draw! ♕\n")
            return True
        elif self.board.is_insufficient_material():
            print("♕ Insufficient material - Draw! ♕\n")
            return True
        elif self.board.is_repetition():
            print("♕ Threefold repetition - Draw! ♕\n")
            return True
        elif self.board.halfmove_clock >= 100:
            print("♕ 50-move rule - Draw! ♕\n")
            return True
        elif self.board.is_check():
            print("⚠️  CHECK! ⚠️\n")
        
        return False
    
    def get_human_move(self):
        """Get move from human player"""
        while True:
            try:
                print(f"Legal moves: {', '.join(self.board.san(m) for m in self.board.legal_moves)}")
                move_input = input("Your move (e.g., e2e4 or e4): ").strip()
                
                if move_input.lower() == "undo" and len(self.game_moves) >= 2:
                    self.board.pop()
                    self.game_moves.pop()
                    self.board.pop()
                    self.game_moves.pop()
                    print("Last move undone (both players).\n")
                    self.display_board()
                    return None
                elif move_input.lower() == "undo" and len(self.game_moves) == 1:
                    self.board.pop()
                    self.game_moves.pop()
                    print("Last move undone.\n")
                    self.display_board()
                    return None
                
                # Try to parse move
                if len(move_input) == 4:
                    move = chess.Move.from_uci(move_input)
                else:
                    move = self.board.parse_san(move_input)
                
                if move in self.board.legal_moves:
                    return move
                else:
                    print("Invalid move! Try again.\n")
            except:
                print("Invalid move format! Use e2e4 or e4 format.\n")
    
    def play_human_vs_bot(self):
        """Play against the bot"""
        print("\n" + "="*50)
        print("HUMAN vs BOT")
        print("="*50)
        
        while True:
            try:
                color = input("Play as White or Black? (w/b): ").lower()
                if color in ['w', 'b']:
                    self.human_color = chess.WHITE if color == 'w' else chess.BLACK
                    break
            except:
                pass
        
        while True:
            try:
                skill = int(input("Bot difficulty (1-4): "))
                if 1 <= skill <= 4:
                    self.bot_skill = skill
                    self.bot = LearningChessBot(skill)
                    break
            except:
                pass
        
        self.board = chess.Board()
        self.game_moves = []
        
        print("\nType 'undo' to undo last move.")
        print("Type 'quit' to resign.\n")
        
        self.display_board()
        
        while True:
            # Check game status
            if self.show_game_status():
                result = self.board.result()
                self.bot.learn_from_game(self.game_moves, result)
                break
            
            if self.board.turn == self.human_color:
                # Human's turn
                print(f"Your turn ({chess.COLOR_NAMES[self.human_color]}):")
                move = self.get_human_move()
                if move is None:
                    self.display_board()
                    continue
            else:
                # Bot's turn
                print(f"Bot is thinking... (Level {self.bot_skill})")
                move = self.bot.get_move(self.board)
                if move:
                    print(f"Bot plays: {self.board.san(move)}")
                else:
                    break
            
            self.board.push(move)
            self.game_moves.append(move)
            self.display_board()
    
    def play_bot_vs_bot(self):
        """Watch bot vs bot"""
        print("\n" + "="*50)
        print("BOT vs BOT")
        print("="*50)
        
        while True:
            try:
                skill1 = int(input("White bot difficulty (1-4): "))
                if 1 <= skill1 <= 4:
                    break
            except:
                pass
        
        while True:
            try:
                skill2 = int(input("Black bot difficulty (1-4): "))
                if 1 <= skill2 <= 4:
                    break
            except:
                pass
        
        bot_white = LearningChessBot(skill1)
        bot_black = LearningChessBot(skill2)
        
        self.board = chess.Board()
        self.game_moves = []
        
        print("\nGame in progress...\n")
        self.display_board()
        
        move_count = 0
        while not self.board.is_game_over():
            move_count += 1
            
            if self.board.turn == chess.WHITE:
                print(f"Move {move_count}: White bot (Level {skill1}) is thinking...")
                move = bot_white.get_move(self.board)
            else:
                print(f"Move {move_count}: Black bot (Level {skill2}) is thinking...")
                move = bot_black.get_move(self.board)
            
            if not move:
                break
            
            print(f"  → {self.board.san(move)}")
            self.board.push(move)
            self.game_moves.append(move)
        
        print("\nGame Over!")
        self.show_game_status()
        
        result = self.board.result()
        bot_white.learn_from_game(self.game_moves, result)
        bot_black.learn_from_game(self.game_moves, result)
        
        self.display_board()
    
    def main_menu(self):
        """Main menu"""
        while True:
            print("\n" + "="*50)
            print("CHESS GAME WITH LEARNING BOT")
            print("="*50)
            print("1. Play against bot")
            print("2. Watch bot vs bot")
            print("3. Quit")
            print("="*50)
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                self.play_human_vs_bot()
                print("\nGame saved to bot knowledge base!\n")
            elif choice == '2':
                self.play_bot_vs_bot()
                print("\nBots learned from this game!\n")
            elif choice == '3':
                print("Thanks for playing! Goodbye!")
                break
            else:
                print("Invalid choice! Try again.")

if __name__ == "__main__":
    game = ChessGame()
    game.main_menu()