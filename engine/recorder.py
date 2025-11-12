from __future__ import annotations
import json
from datetime import datetime
import chess
import chess.pgn
from typing import List


class GameRecorder:
    """
        Class to record chess game positions and moves in FEN and PGN formats.
        It allows taking snapshots of board positions, adding moves, and saving to files.
    """

    # Constructor
    def __init__(self):
        """
            Initializes the GameRecorder object.
            Parameters:
                - self: GameRecorder instance
        """

        # Initialize list to store FEN positions
        self.positions_fen: List[str] = []

        # Initialize PGN game
        self.pgn_game = chess.pgn.Game()

        # Set PGN headers
        self.pgn_game.headers["Event"] = "Human vs. MiniMax"
        self.pgn_game.headers["Site"] = "Local"
        self.pgn_game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        self.pgn_game.headers["White"] = "You"
        self.pgn_game.headers["Black"] = "MiniMax"
        
        # Current pointereto the node in the PGN tree
        self.node = self.pgn_game

    # Take a snapshot of the current board position in FEN
    def snapshot(self, board: chess.Board) -> None:
        """
            Save the current board position in FEN format.
            Parameters:
                - self: GameRecorder instance
                - board: chess.Board instance
            Returns:
                - None
        """

        # Append current FEN to the list
        self.positions_fen.append(board.fen())

    # Add a move to the PGN game
    def add_move(self, move: chess.Move, board_before: chess.Board) -> None:
        """
            Add a move to the PGN game.
            Parameters:
                - self: GameRecorder instance
                - move: chess.Move instance
                - board_before: chess.Board instance before the move
            Returns:
                - None
        """
        # Advance PGN node with the played move
        self.node = self.node.add_variation(move)

    # Save all recorded positions and PGN game to files
    def save_all(self, fen_path: str = "positions.json", pgn_path: str = "game.pgn") -> None:
        """
            Save recorded FEN positions to a JSON file and PGN game to a PGN file.
            Parameters:
                - self: GameRecorder instance
                - fen_path: path to save FEN positions JSON
                - pgn_path: path to save PGN game file
            Returns:
                - None
        """

        # Save FEN positions to JSON file
        with open(fen_path, "w", encoding="utf-8") as f:
            json.dump(self.positions_fen, f, ensure_ascii=False, indent=2)
        # Save PGN game to PGN file
        with open(pgn_path, "w", encoding="utf-8") as f:
            print(self.pgn_game, file=f)
