# 🏆 Chess Master - Professional Chess Game

A sophisticated, tournament-quality chess implementation built with Python and Pygame, featuring authentic Staunton-style pieces, intelligent AI opponents, and a beautiful wooden board aesthetic.

![Chess Master](https://img.shields.io/badge/Chess-Master-gold?style=for-the-badge&logo=chess)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.6+-green?style=for-the-badge&logo=pygame)

## 🎯 Features

### ♟️ Complete Chess Implementation
- **100% Accurate Chess Rules** - All standard chess moves and regulations
- **Special Moves** - En passant, castling (kingside & queenside), pawn promotion
- **Game State Detection** - Check, checkmate, and stalemate recognition
- **Legal Move Validation** - Prevents illegal moves that would leave king in check

### 🎨 Professional Visual Design
- **Authentic Staunton Pieces** - Traditional tournament-style chess piece designs
- **Tournament Board** - Wooden aesthetic with coordinate labels (a-h, 1-8)
- **Visual Feedback** - Golden selection highlights, green move indicators, red check warnings
- **Elegant UI** - Professional typography and wood-grain sidebar

### 🤖 Intelligent AI System
- **4 Difficulty Levels** - Easy, Medium, Hard, Expert
- **Minimax Algorithm** - With alpha-beta pruning for optimal performance
- **Strategic Evaluation** - Considers piece values and positional advantages
- **Adaptive Gameplay** - From random moves to 4-ply deep analysis

### 🎮 Game Modes
- **Player vs Player** - Local multiplayer chess
- **Player vs AI** - Challenge computer opponents
- **New Game** - Quick restart functionality
- **Mode Switching** - Easy toggling between game types

## 🚀 Quick Start

### Project Structure
```
chess/
├── enhanced_chess_game.py    # Main game file
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies
├── run_chess.bat            # Windows launcher script
├── run_chess.sh             # Linux/macOS launcher script
├── .gitignore               # Git ignore rules
└── output/                  # Build output directory
```

### Prerequisites
- Python 3.11 or higher
- Pygame 2.6 or higher

### Installation

1. **Clone or download** the chess game files
2. **Install dependencies**:
   ```bash
   # Option 1: Using requirements.txt (recommended)
   pip install -r requirements.txt
   
   # Option 2: Manual installation
   pip install pygame
   ```
3. **Run the game**:
   ```bash
   # Method 1: Direct Python execution
   python enhanced_chess_game.py
   
   # Method 2: Using convenience scripts
   # Windows:
   run_chess.bat
   
   # Linux/macOS:
   chmod +x run_chess.sh
   ./run_chess.sh
   ```

## 🎯 How to Play

### Basic Controls
- **Click** on a piece to select it
- **Click** on a highlighted square to move
- **Click** buttons in the sidebar to change settings

### Game Features
- **Turn Indicator** - Shows whose turn it is with visual piece icon
- **Check Warning** - King flashes red when in check
- **Move History** - Last move displayed in algebraic notation
- **Move Counter** - Tracks game progress
- **AI Thinking** - Animated indicator when AI is calculating

### Visual Indicators
- 🟡 **Golden Glow** - Selected piece
- 🟢 **Green Circles** - Possible moves
- 🔴 **Red Flash** - King in check
- 🟠 **Orange Highlight** - Last move made

## 🏗️ Technical Architecture

### Core Components

#### `Piece` Class
- Individual piece logic and movement rules
- Legal move generation with check validation
- Special move handling (castling, en passant)

#### `ChessAI` Class
- Minimax algorithm with alpha-beta pruning
- Position evaluation with piece-square tables
- Difficulty scaling through search depth

#### `ChessGame` Class
- Game state management
- Move execution and validation
- UI rendering and event handling

#### `Button` Class
- Interactive UI elements
- Hover effects and click handling
- Professional styling

### Chess Rules Implementation

#### Standard Moves
```python
# Pawn movement with double-move and capture logic
# Knight L-shaped movement (2+1 squares)
# Bishop diagonal sliding
# Rook horizontal/vertical sliding  
# Queen combined rook+bishop movement
# King single-square movement
```

#### Special Moves
```python
# En passant capture detection
# Castling safety verification
# Pawn promotion to queen
```

#### Game State
```python
# Check detection algorithm
# Checkmate/stalemate evaluation
# Legal move filtering
```

## 🎨 Visual Design Details

### Authentic Staunton Pieces
Each piece is meticulously designed to match traditional tournament chess sets:

- **♟️ Pawn** - Rounded head with tapered body and stable base
- **♞ Knight** - Horse head in profile with mane details
- **♗ Bishop** - Traditional mitre with liturgical cross
- **♜ Rook** - Castle turret with crenellations
- **♛ Queen** - Multi-pointed crown with royal jewels
- **♚ King** - Royal crown with cross finial and orb

### Color Scheme
- **Board Squares** - Rich wooden brown and cream colors
- **Piece Colors** - Pure white and deep black with realistic shading
- **UI Elements** - Elegant gold accents and warm earth tones
- **Highlights** - Professional tournament-style indicators

## 🧠 AI Difficulty Levels

| Level | Depth | Description | Best For |
|-------|--------|-------------|----------|
| **Easy** | Random | Random legal moves | Beginners |
| **Medium** | 2-ply | Basic strategy | Casual players |
| **Hard** | 3-ply | Strong tactical play | Intermediate |
| **Expert** | 4-ply | Advanced strategy | Experienced players |

### AI Features
- **Position Evaluation** - Considers material and positional factors
- **Opening Principles** - Encourages piece development
- **Tactical Awareness** - Looks for captures and threats
- **Strategic Planning** - Multi-move combinations

## 📋 Chess Notation

The game displays moves in standard algebraic notation:
- **Basic Moves** - e4, Nf3, Bc4
- **Captures** - exd5, Nxf7
- **Castling** - O-O (kingside), O-O-O (queenside)
- **Check** - +
- **Unicode Pieces** - ♔♕♖♗♘♙

## 🎛️ Customization Options

### Game Settings
- Switch between Player vs Player and Player vs AI
- Adjust AI difficulty level
- Start new games instantly
- Visual feedback preferences

### Visual Elements
- Professional tournament board design
- Authentic piece styling
- Coordinate labels for notation
- Move history tracking

## 🔧 System Requirements

### Minimum Requirements
- **OS** - Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python** - 3.11 or higher
- **RAM** - 512 MB
- **Storage** - 50 MB
- **Display** - 1024x768 resolution

### Recommended
- **RAM** - 1 GB for smoother AI performance
- **Display** - 1280x720 or higher for optimal experience

## 🐛 Troubleshooting

### Common Issues

**Game won't start:**
```bash
# Check Python version
python --version

# Install/update Pygame
python -m pip install --upgrade pygame
```

**Slow AI performance:**
- Reduce AI difficulty level
- Close other applications
- Ensure adequate system resources

**Visual issues:**
- Update graphics drivers
- Check display resolution
- Verify color depth settings

## 🤝 Contributing

This is a complete chess implementation with room for enhancements:

### Potential Improvements
- **Save/Load Games** - PGN format support
- **Online Multiplayer** - Network play capability
- **Opening Book** - Database of chess openings
- **Endgame Tablebase** - Perfect endgame play
- **Analysis Mode** - Move suggestion and evaluation
- **Themes** - Additional board and piece styles

### Code Structure
The code is well-organized and documented for easy modification:
- Clean class separation
- Comprehensive comments
- Modular design
- Extensible architecture

## 📄 License

This chess game is provided as educational software. Feel free to use, modify, and distribute for learning purposes.

## 🏆 Credits

**Chess Master** - A sophisticated chess implementation showcasing:
- Advanced game programming techniques
- Professional UI/UX design
- Artificial intelligence algorithms
- Traditional chess aesthetics

**Made by jihad**

Built with ❤️ using Python and Pygame.

---

### 🎯 Ready to Play?

Experience tournament-quality chess with authentic visuals and intelligent opponents!

```bash
python enhanced_chess_game.py
```

**Good luck, and may the best player win!** ♔
