import tkinter as tk
import chess
import os

from engine.evaluation import Evaluator
from engine.search import NegamaxEngine

# Visual configuration
SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"

# Pieces Unicode
WHITE_PIECES = {
    chess.PAWN: "♙",
    chess.KNIGHT: "♘",
    chess.BISHOP: "♗",
    chess.ROOK: "♖",
    chess.QUEEN: "♕",
    chess.KING: "♔",
}
BLACK_PIECES = {
    chess.PAWN: "♟",
    chess.KNIGHT: "♞",
    chess.BISHOP: "♝",
    chess.ROOK: "♜",
    chess.QUEEN: "♛",
    chess.KING: "♚",
}


class ChessGUI:
    """
        Class to create a GUI for human vs computer chess game.
        Also synchronizes each move with external files for a robot:
        - initialMove.txt -> from-square (e.g., 'a1')
        - finalMove.txt   -> to-square   (e.g., 'a5')
        The game only continues when both files have been deleted.
    """

    # Constructor
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI Chess - Human vs Computer")

        # Logical chess setup
        self.board = chess.Board()
        evaluator = Evaluator(mobility_weight=3)
        self.engine = NegamaxEngine(evaluator=evaluator, depth=3)

        # State of player selection
        self.selected_square = None  # Stores an index 0–63 or None

        # Flag to control if human is allowed to move
        self.can_human_move = True

        # Canvas to draw the board
        self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        # Info label
        self.info_label = tk.Label(root, text="Turn: white (Human)")
        self.info_label.pack(pady=5)

        # Initial board draw
        self.draw_board()

    # Helper method for robot sync

    def write_move_files(self, move: chess.Move):
        """
            Create/overwrite initialMove.txt and finalMove.txt with
            the from/to squares of the given move (e.g., 'a1', 'a5').
        """

        # Remove old files if they exist
        for fname in ("initialMove.txt", "finalMove.txt"):
            if os.path.exists(fname):
                os.remove(fname)

        from_sq_name = chess.square_name(move.from_square)  # e.g., 'a1'
        to_sq_name = chess.square_name(move.to_square)      # e.g., 'a5'

        with open("initialMove.txt", "w", encoding="utf-8") as f:
            f.write(from_sq_name)

        with open("finalMove.txt", "w", encoding="utf-8") as f:
            f.write(to_sq_name)

        print(f"[Files] initialMove.txt = {from_sq_name}, finalMove.txt = {to_sq_name}")

    # Wait until both move files are deleted
    def wait_until_files_deleted(self, callback):
        """
            Periodically checks if initialMove.txt and finalMove.txt
            no longer exist. When both are deleted, calls `callback`.
        """
        initial_exists = os.path.exists("initialMove.txt")
        final_exists = os.path.exists("finalMove.txt")

        # Both files are gone -> external system finished using the move
        if not initial_exists and not final_exists:
            callback()
        # Check again in 200 ms
        else:
            self.root.after(200, lambda: self.wait_until_files_deleted(callback))

    def after_human_move_ready(self):
        """
            Called when the robot/external system has finished
            processing the human move (files deleted).
            Now it's time for the computer to move.
        """
        if self.board.is_game_over():
            self.show_result()
            return

        self.info_label.config(text="Turn: black (Computer)")
        
        # Let the AI make its move
        self.computer_move()

    def after_ai_move_ready(self):
        """
            Called when the robot/external system has finished
            processing the computer move (files deleted).
            Now it's time for the human to move again.
        """
        if self.board.is_game_over():
            self.show_result()
            return

        self.can_human_move = True
        self.info_label.config(text="Turn: white (Human)")

    # Board drawing method
    def draw_board(self):
        """
            Draw the chess board and pieces on the canvas.
            Parameters:
                - self: ChessGUI instance
            Returns:
                - None
        """

        # Clear the canvas
        self.canvas.delete("all")

        # Draw squares and pieces
        for rank in range(8):
            for file in range(8):

                # Calculate square coordinates
                x1 = file * SQUARE_SIZE
                y1 = (7 - rank) * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                # Determine square color
                color = LIGHT_COLOR if (file + rank) % 2 == 0 else DARK_COLOR
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Draw piece if present
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if piece:
                    if piece.color == chess.WHITE:
                        symbol = WHITE_PIECES[piece.piece_type]
                    else:
                        symbol = BLACK_PIECES[piece.piece_type]

                    # Draw the piece symbol
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=symbol,
                        font=("Arial", 32),
                    )

        # Highlight selected square
        if self.selected_square is not None:
            file = chess.square_file(self.selected_square)
            rank = chess.square_rank(self.selected_square)
            x1 = file * SQUARE_SIZE
            y1 = (7 - rank) * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="red", width=3
            )

    # User click handling
    def on_click(self, event):
        """
            Handle user clicks on the chess board.
            Parameters:
                - self: ChessGUI instance
                - event: Tkinter event instance
            Returns:
                - None
        """

        # Ignore clicks if game is over
        if self.board.is_game_over():
            return

        # If we are waiting for the robot, ignore clicks
        if not self.can_human_move:
            return

        # Only allow moving if it's white's turn (human)
        if self.board.turn != chess.WHITE:
            return

        # Calculate clicked square
        file = event.x // SQUARE_SIZE
        rank = 7 - (event.y // SQUARE_SIZE)

        # Check bounds
        if file < 0 or file > 7 or rank < 0 or rank > 7:
            return

        # Calculate the square index
        clicked_square = chess.square(file, rank)

        # Handle first and second clicks
        if self.selected_square is None:
            # First click: select piece
            piece = self.board.piece_at(clicked_square)
            if piece is None or piece.color != chess.WHITE:
                return
            self.selected_square = clicked_square
            self.draw_board()
        else:
            # Second click: attempt to move
            from_sq = self.selected_square
            to_sq = clicked_square
            move = chess.Move(from_sq, to_sq)

            # Check if move is legal, handle promotion
            if move not in self.board.legal_moves:
                promo_move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
                if promo_move in self.board.legal_moves:
                    move = promo_move
                else:
                    # Illegal move, deselect
                    self.selected_square = None
                    self.draw_board()
                    return

            # Make the move made by the human
            print(f"Move (Human): {move.uci()}")
            self.board.push(move)
            self.selected_square = None
            self.draw_board()

            # Send move to robot via files
            self.can_human_move = False
            self.write_move_files(move)
            self.info_label.config(
                text="Human move sent (initialMove.txt / finalMove.txt). Waiting external execution..."
            )

            # Check for game over
            if self.board.is_game_over():
                self.show_result()
                return

            # Wait until files are deleted, then continue with computer move
            self.wait_until_files_deleted(self.after_human_move_ready)

    # AI move handling 
    def computer_move(self):
        """
            Let the computer (AI) make its move.
            Parameters:
                - self: ChessGUI instance
            Returns:
                - None
        """

        # Ignore if game is over
        if self.board.is_game_over():
            return

        # Get AI move
        move = self.engine.choose_move(self.board)
        if move is None:
            self.show_result()
            return

        # Make the AI move
        print(f"Move (Computer): {move.uci()}")
        move_san = self.board.san(move)
        self.board.push(move)
        self.draw_board()

        # Send AI move to robot via files
        self.can_human_move = False
        self.write_move_files(move)
        self.info_label.config(
            text=f"Black plays: {move_san}. Waiting external execution of AI move..."
        )

        # Check for game over
        if self.board.is_game_over():
            self.show_result()
            return

        # Wait until files are deleted, then give turn back to human
        self.wait_until_files_deleted(self.after_ai_move_ready)

    # Show game result
    def show_result(self):
        """
            Display the result of the game.
            Parameters:
                - self: ChessGUI instance
            Returns:
                - None
        """

        # Get and display result
        result = self.board.result()

        # Display result message
        if result == "1-0":
            text = "Result: 1-0 (white wins)"
        elif result == "0-1":
            text = "Result: 0-1 (black wins)"
        else:
            text = "Result: 1/2-1/2 (draw)"
        self.info_label.config(text=text)
