from __future__ import annotations
import random
import chess
from typing import Optional, Tuple
from .evaluation import Evaluator


class NegamaxEngine:
    """
        Class implementing a Negamax search engine with alpha-beta pruning.
        It uses an injected Evaluator instance to evaluate board positions.
        Chooses the best move by searching up to a specified depth.
    """

    # Constructor
    def __init__(self, evaluator: Evaluator, depth: int = 3):
        """
        Initializes the Negamax engine.
        Parameters:
            - self: NegamaxEngine instance
            - evaluator: Evaluator instance 
            - depth: default search depth
        """

        # Initialize evaluator and depth
        self.evaluator = evaluator
        self.depth = depth

    # Choose the best move
    def choose_move(self, board: chess.Board, depth: Optional[int] = None) -> Optional[chess.Move]:
        """
            Pick the best move for the current player by searching up to `depth`.
            Falls back to a random legal move if none found (e.g., no legal moves).
            Parameters:
                - self: NegamaxEngine instance
                - board: chess.Board instance
                - depth: optional search depth (overrides default if provided)
            Returns:
                - Optional[chess.Move]: best move found or None
        """

        # Determine search depth
        d = depth if depth is not None else self.depth

        # Start negamax search
        score, move = self._negamax(board, d, -10**9, 10**9)
        
        # Return the chosen move or a random legal move
        if move is None:
            legal = list(board.legal_moves)
            return random.choice(legal) if legal else None
        return move

    # Negamax search with alpha-beta pruning
    def _negamax(self, board: chess.Board, depth: int, alpha: int, beta: int) -> Tuple[int, Optional[chess.Move]]:
        """
            Search the best move using Negamax with alpha-beta pruning.
            Use recursion up to `depth` returning the best score and move.
            Parameters:
                - self: NegamaxEngine instance
                - board: chess.Board instance
                - depth: current search depth
                - alpha: alpha value for pruning
                - beta: beta value for pruning
            Returns:
                - Tuple[int, Optional[chess.Move]]: best score and corresponding move
        """

        # Base case
        if depth == 0 or board.is_game_over():
            return self.evaluator.evaluate(board), None

        # Initialize best score and move
        best_score = -10**9
        best_move: Optional[chess.Move] = None

        # Order moves to improve pruning efficiency
        moves = list(board.legal_moves)

        # Simple move ordering: captures and promotions first
        def move_score(m: chess.Move) -> int:
            if board.is_capture(m):
                return 1000
            if m.promotion:
                return 900
            return 0

        # Sort moves by their score
        moves.sort(key=move_score, reverse=True)

        # Explore each move by recursion
        for move in moves:
            board.push(move)
            score, _ = self._negamax(board, depth - 1, -beta, -alpha)
            score = -score
            board.pop()

            # Update best score and move
            if score > best_score:
                best_score = score
                best_move = move

            # alpha-beta pruning
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

        # Return the best score and move found
        return best_score, best_move
