from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen=True)
class GameState:
    n: int
    score: int = 0
    bank: int = 0
    turn: int = 0  # 0=cilvēks, 1=AI

def legal_moves(state: GameState) -> List[int]:
    return [d for d in (3, 4, 5) if state.n % d == 0]

def apply_move(state: GameState, move: int) -> GameState:
    if move not in (3, 4, 5):
        raise ValueError("Move must be 3, 4, or 5.")
    if state.n % move != 0:
        raise ValueError("Illegal move for current number.")
    new_n = state.n // move
    new_score = state.score + (1 if new_n % 2 == 0 else -1)
    new_bank = state.bank + (1 if new_n % 10 in (0, 5) else 0)
    return GameState(n=new_n, score=new_score, bank=new_bank, turn=1 - state.turn)

def is_terminal(state: GameState) -> bool:
    return len(legal_moves(state)) == 0

def final_result(state: GameState) -> Dict[str, Any]:
    final_score = state.score - state.bank if state.score % 2 == 0 else state.score + state.bank
    winner = "Cilvēks (1. spēlētājs)" if final_score % 2 == 0 else "AI (2. spēlētājs)"
    return {
        "raw_score": state.score,
        "bank": state.bank,
        "final_score": final_score,
        "winner": winner,
        "winner_is_ai": winner.startswith("AI"),
    }