from __future__ import annotations
import chess
from typing import Dict


class Evaluator:
    """
        Class to evaluate chess board positions and give a
        proper score to decide a best move.
    """

    # Base piece values 
    PIECE_VALUES: Dict[int, int] = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0,
    }

    # Constructor 
    def __init__(self, mobility_weight: int = 3):
        """
            Initializes the evaluator object.
            Parameters:
                - self: evaluator instance
                - mobility_weight: bonus per legal move for side-to-move
        """
        
        # Initialize mobility weight
        self.mobility_weight = mobility_weight

    # Static evaluation method
    def evaluate(self, board: chess.Board) -> int:
        """
            Static evaluation from side-to-move perspective.
            It saves the position of the board and returns a score.
            Parameters:
                - self: evaluator instance
                - board: chess.Board instance
            Returns:
                - int: score of the position
        """

        # Initialize score
        score = 0

        # Sum material value
        for piece in board.piece_map().values():
            val = self.PIECE_VALUES[piece.piece_type]
            score += val if piece.color == chess.WHITE else -val

        # Mobility bonus if side-to-move
        mobility = len(list(board.legal_moves))
        score += self.mobility_weight * (mobility if board.turn == chess.WHITE else -mobility)

        # Detect terminal states of a checkmate and return large scores
        if board.is_checkmate():
            return -999_999 if board.turn else 999_999
        # Detect stalemate or insufficient material or draw by repetition and return 0
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
            return 0

        # Return the final score
        return score
