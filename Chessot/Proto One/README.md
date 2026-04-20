# Advanced Chess Engine with Learning J Bot

A fully-featured chess game with an AI opponent that learns and improves over time. Built with Python using the `python-chess` library.

## Features

### ✨ Complete Chess Rule Support
- **Checkmate & Stalemate**: Proper game termination detection
- **Check Detection**: Real-time check status
- **En Passant**: Automatic en passant capture recognition
- **Pawn Promotion**: Interactive promotion selection (Queen/Rook/Bishop/Knight)
- **Castling**: Full castling rights support
- **50-Move Rule**: Draw detection by move repetition
- **Threefold Repetition**: Draw detection by position repetition
- **Insufficient Material**: Draw detection for endgame scenarios

### 🤖 Advanced Chess Engine

**Minimax Algorithm with Alpha-Beta Pruning**
- Efficient game tree search
- Move ordering for better pruning
- Configurable search depth (difficulty levels 1-4)

**Sophisticated Board Evaluation**
- Material evaluation with standard piece values
- Piece-square tables for positional understanding
- Mobility evaluation (number of legal moves)
- King safety assessment
- Check/checkmate detection bonuses

**Transposition Table**
- Caches previously evaluated positions
- Speeds up repeated position analysis
- Clears between searches for freshness

**Move Ordering Heuristics**
- Prioritizes capture moves
- Prioritizes checking moves
- Improves alpha-beta pruning efficiency

**Opening Book**
- Common opening positions with strong moves
- Includes e4, d4, and Sicilian/Italian variations
- Quick response in opening phase
- Falls back to minimax for unfamiliar positions

### 📚 Learning System

**Position Learning**
The bot learns from every game played:
- Stores game outcomes and positions
- Saves knowledge to `bot_knowledge.json`
- Learns winning patterns over time
- Gets stronger as you play more games

**Player Pattern Recognition** 🎯 NEW
- Tracks every move you make in each position
- Records your win/loss/draw statistics by move
- Saves patterns to `player_patterns.json`
- Learns your opening preferences
- Identifies your weak positions and tactics
- Adapts strategy to exploit your weaknesses
- **Gets better at beating YOU specifically over time!**

### 🎮 User Interfaces

#### GUI (JBot.py)
- Clean, modern Tkinter interface with cool-tone color palette
- 8x8 chess board with coordinates
- Visual move highlighting and selection
- **Board orientation**: Flips perspective when playing as Black
- Real-time evaluation bar (White/Black advantage) - **Toggleable**
- **Larger board display** for better visibility (600x600 canvas)
- Game information panel:
  - FEN notation
  - Turn indicator
  - Game status (Check, Checkmate, Stalemate, etc.)
  - Legal move count
- Move history in algebraic notation
- Undo functionality
- Difficulty slider (1-4)
- Three game modes:
  - **Human vs Bot**: Play against the AI (White or Black)
  - **Bot vs Bot**: Watch two AI players compete at different difficulty levels
  - **New Game**: Start a fresh match with configurable difficulty
- Difficulty slider (1-4) with live updates
- Eval bar toggle (ON/OFF) to save screen space

#### Command-Line (Main.py)
- Text-based chess interface
- Move input in standard notation (e.g., `e2e4` or `e4`)
- Full move history display
- Undo support
- Human vs Bot and Bot vs Bot modes
- Interactive game menu

### 📊 Game Analysis

**Real-time Evaluation Bar**
- Shows position advantage visually
- White at top, Black at bottom
- Normalized score display
- Updates after every move

**Game Information Display**
- FEN (Forsyth-Edwards Notation)
- Current turn
- Halfmove clock (for 50-move rule)
- Fullmove number
- Game status alerts
- Available bot difficulty

## File Structure

```
Proto One/
├── ChessBot.py         # Advanced chess engine with learning
├── JBot.py            # Modern GUI with cool-tone design
├── Main.py            # Command-line interface
├── test_chess.py      # Test suite
├── bot_knowledge.json     # Learned positions (auto-generated)
└── player_patterns.json   # Your playstyle analysis (auto-generated)
```

## How to Use

### GUI Version (Recommended)
```bash
python JBot.py
```
1. Select difficulty level (1-4)
2. Choose your color or watch bot vs bot
3. Click to select pieces, highlighted squares show valid moves
4. Click destination to move
5. Press "New Game" to start fresh

### Command-Line Version
```bash
python Main.py
```
1. Select game mode (Human vs Bot or Bot vs Bot)
2. Enter your preferences
3. Type moves in standard notation (e.g., `e2e4` or just `e4`)
4. Type `undo` to undo your last move
5. Type `quit` to resign

## Difficulty Levels

| Level | Search Depth | Speed | Strength |
|-------|-------------|-------|----------|
| 1     | 2 plies     | Very Fast | Easy |
| 2     | 4 plies     | Fast | Intermediate |
| 3     | 6 plies     | Moderate | Hard |
| 4     | 8 plies     | Slow | Very Hard |

**Note**: The bot gets stronger over time as it learns winning patterns from each game!

## Move Notation

The game accepts moves in two formats:
- **Long form**: `e2e4` (from e2 to e4)
- **Short form**: `e4` (moving to e4, in algebraic notation)

For pawn promotion, the game will prompt you to choose a piece.

## Learning System

**Persistent Knowledge** (`bot_knowledge.json`)
- Stores all encountered positions
- Win/loss/draw statistics for each position
- Improves evaluation accuracy over time

**Player-Specific Learning** (`player_patterns.json`) 🎯 NEW
- Tracks every move you play in each position
- Records success rate for each of your moves
- Bot learns your favorite openings
- Bot learns which positions you struggle in
- Bot learns your tactical patterns
- **The bot becomes increasingly tailored to beat YOUR playstyle**

Both files persist across sessions - the bot remembers you and gets progressively better at defeating your specific approach!

## Technical Details

### Engine Algorithm
- **Search**: Minimax with Alpha-Beta Pruning
- **Depth**: Adaptive based on difficulty level
- **Evaluation**: Comprehensive position evaluation function
- **Caching**: Transposition tables for efficiency

### Chess Library
- Uses the `python-chess` library (v1.11.2+)
- Handles all chess rules automatically
- Provides FEN notation support

### Requirements
- Python 3.x
- `python-chess` library (install with: `pip install python-chess`)
- Tkinter (usually included with Python)

## Example Game

```
Initial Position

 8  ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜
 7  ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟
 6  . . . . . . . .
 5  . . . . . . . .
 4  . . . . . . . .
 3  . . . . . . . .
 2  ♙ ♙ ♙ ♙ ♙ ♙ ♙ ♙
 1  ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖
    a b c d e f g h

White: e4
Black (Bot Level 2): e5
...
```

## Features Demonstration

### Checkmate Detection
The engine correctly identifies checkmate positions and prevents illegal moves into check.

### Pawn Promotion
When a pawn reaches the opponent's back rank, the player is prompted to choose a promotion piece.

### En Passant
Automatic en passant capture is recognized and executed when legal.

### Learning
After each game, the bot analyzes all positions reached and improves its evaluation of similar positions in future games.

## Tips for Playing

1. **Watch It Learn**: Play multiple games and watch the bot adapt to your style
2. **Check Player Patterns**: Look at `player_patterns.json` to see what the bot has learned about you
3. **Vary Your Strategy**: Try different openings to challenge the bot's learning
4. **Increase Difficulty**: Use the difficulty slider to challenge yourself as you improve
5. **Watch Bot vs Bot**: Observe high-level play at level 3-4 to learn strong positions
6. **Use Undo**: Practice different strategies by undoing moves
7. **Check Status**: Watch the evaluation bar to understand position advantages
8. **Play Black**: Try playing as Black and notice how the board flips for your perspective

## Troubleshooting

**"No module named 'chess'"**: Install python-chess with `pip install python-chess`

**GUI not appearing**: Make sure you have Tkinter installed (usually comes with Python)

**Bot taking too long**: Lower the difficulty level for faster moves

**Learning not working**: Ensure the script has write permissions in its directory

## Future Enhancements

Potential improvements could include:
- Expanded opening book with more variations
- Endgame tablebases for perfect endgame play
- UCI/Stockfish engine integration for comparison
- Network multiplayer support
- Game saving/loading with PGN format
- More sophisticated neural network evaluation
- Cloud-based learning to share patterns across players
- Mobile app version

## License

Free to use and modify for educational purposes.

## Credits

Built with:
- `python-chess`: Python chess library
- `tkinter`: GUI framework
- Minimax algorithm with Alpha-Beta pruning

Enjoy your chess games! ♔
