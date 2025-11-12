import chess
from engine.evaluation import Evaluator
from engine.search import NegamaxEngine
from engine.recorder import GameRecorder

# Main function to run the chess game
def main():
    """
        Main loop for a human vs. computer chess game.
    """

    # GUI header for user
    print("=== CHESS: human (white) vs computer (black) ===")
    print("Commands: 'fen' (state), 'help' (examples), 'quit' (end)\n")

    # Initialize board and recorder
    board = chess.Board()
    rec = GameRecorder()
    rec.snapshot(board)

    # Build engine from classes
    eval_ = Evaluator(mobility_weight=3)
    engine = NegamaxEngine(evaluator=eval_, depth=3)

    # Main game loop
    while not board.is_game_over():
        
        # Display board
        print(board)
        print(f"Turn of {'White' if board.turn == chess.WHITE else 'Black'}")

        # If it's white's turn (human)
        if board.turn == chess.WHITE:
            user = input("Your move: ").strip()

            # Handle user commands
            if user.lower() in ("quit", "exit", "q"):
                print("Match ended by user.")
                break

            # Show FEN or help
            if user.lower() == "fen":
                print("FEN:", board.fen(), "\n")
                continue

            # Show help
            if user.lower() == "help":
                print("UCI: e2e4, g1f3, e7e8q | SAN: e4, Nf3, exd5, O-O\n")
                continue

            # Parse and make the move in SAN format
            try:
                move = board.parse_san(user)

            # Handle invalid moves
            except ValueError:
                # Try UCI format
                try:
                    move = chess.Move.from_uci(user)
                    if move not in board.legal_moves:
                        raise ValueError("Illegal move")
                # Handle invalid UCI
                except Exception:
                    print("Invalid move. Try again.")
                    continue

            # Make the move and record it
            board_before = board.copy()
            board.push(move)
            rec.add_move(move, board_before)
            rec.snapshot(board)

        # Computer's turn (black)
        else:
            # Choose and make the best move
            print("Thinking...")
            move = engine.choose_move(board)

            # Handle no legal moves
            if move is None:
                print("No legal moves.")
                break

            # Make the move and record it
            board_before = board.copy()
            move_san = board.san(move)
            board.push(move)
            print(f"Computer plays: {move_san}\n")
            rec.add_move(move, board_before)
            rec.snapshot(board)

    # Game over handling
    if board.is_game_over():
        # Display final board and result
        print(board)
        print("Result:", board.result(), "(1-0 White, 0-1 Black, 1/2-1/2 Draw)")
    
    # Save recorded game
    rec.save_all()
    print("Game saved in positions.json and game.pgn")

# Run main function
if __name__ == "__main__":
    main()
