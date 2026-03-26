# ai_player.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import time

from engine import GameState, legal_moves, apply_move, is_terminal, final_result


@dataclass
class SearchStats:
    generated_nodes: int = 0
    evaluated_nodes: int = 0
    total_ai_time: float = 0.0
    ai_moves: int = 0

    def reset(self) -> None:
        self.generated_nodes = 0
        self.evaluated_nodes = 0
        self.total_ai_time = 0.0
        self.ai_moves = 0

    @property
    def avg_ai_move_time(self) -> float:
        return self.total_ai_time / self.ai_moves if self.ai_moves else 0.0


@dataclass
class Node:
    state: GameState
    move: Optional[int] = None
    depth: int = 0
    children: List["Node"] = field(default_factory=list)
    value: Optional[float] = None


def heuristic(state: GameState) -> float:
    """
    Heiristika depth-limit gadījumā.
    Lietojam score + neliels bankas svars + mobilitāte (gājienu skaits).
    """
    mobility = len(legal_moves(state))
    return (state.score * 1.0) + (state.bank * 0.25) + (mobility * 0.1)


def terminal_utility_for_ai(state: GameState) -> float:
    """
    Termināla vērtība AI perspektīvā: +1 ja AI uzvar, -1 ja AI zaudē.
    """
    r = final_result(state)
    return 1.0 if r.get("winner_is_ai", False) else -1.0


def build_tree(root_state: GameState, depth: int, stats: Optional[SearchStats] = None) -> Node:
    """
    Uzbūvē spēles koku līdz depth, glabājot Node/children datu struktūrā.
    """
    if stats is None:
        stats = SearchStats()

    def _build(state: GameState, d: int, current_depth: int) -> Node:
        node = Node(state=state, move=None, depth=current_depth)
        stats.generated_nodes += 1

        if d == 0 or is_terminal(state):
            return node

        for m in legal_moves(state):
            child_state = apply_move(state, m)
            child = _build(child_state, d - 1, current_depth + 1)
            child.move = m
            node.children.append(child)

        return node

    return _build(root_state, depth, 0)


def minimax_on_tree(node: Node, depth: int, maximizing_ai: bool, stats: SearchStats) -> float:
    state = node.state

    if depth == 0 or is_terminal(state) or not node.children:
        stats.evaluated_nodes += 1
        return terminal_utility_for_ai(state) if is_terminal(state) else heuristic(state)

    if maximizing_ai:
        best = float("-inf")
        for ch in node.children:
            best = max(best, minimax_on_tree(ch, depth - 1, False, stats))
        node.value = best
        return best
    else:
        best = float("inf")
        for ch in node.children:
            best = min(best, minimax_on_tree(ch, depth - 1, True, stats))
        node.value = best
        return best


def alphabeta_on_tree(node: Node, depth: int, alpha: float, beta: float, maximizing_ai: bool, stats: SearchStats) -> float:
    state = node.state

    if depth == 0 or is_terminal(state) or not node.children:
        stats.evaluated_nodes += 1
        return terminal_utility_for_ai(state) if is_terminal(state) else heuristic(state)

    if maximizing_ai:
        value = float("-inf")
        for ch in node.children:
            value = max(value, alphabeta_on_tree(ch, depth - 1, alpha, beta, False, stats))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        node.value = value
        return value
    else:
        value = float("inf")
        for ch in node.children:
            value = min(value, alphabeta_on_tree(ch, depth - 1, alpha, beta, True, stats))
            beta = min(beta, value)
            if alpha >= beta:
                break
        node.value = value
        return value


def tree_to_text(node: Node, max_depth: int = 6) -> str:
    """
    Eksportē koku kā indentuotu tekstu.
    """
    lines: List[str] = []

    def _walk(n: Node, d: int) -> None:
        s = n.state
        mv = "-" if n.move is None else str(n.move)
        val = "" if n.value is None else f" val={n.value:.3f}"
        lines.append(
            "  " * d + f"[d={d}] move={mv} n={s.n} score={s.score} bank={s.bank} turn={s.turn}{val}"
        )
        if d >= max_depth:
            return
        for ch in n.children:
            _walk(ch, d + 1)

    _walk(node, 0)
    return "\n".join(lines)


def save_tree_txt(root: Node, filename: str = "last_game_tree.txt", max_depth: int = 6) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(tree_to_text(root, max_depth=max_depth))


def choose_move(
    state: GameState,
    algorithm: str = "alphabeta",
    depth: int = 6,
    stats: Optional[SearchStats] = None,
    return_tree: bool = False,
):
    """
    Atgriež AI gājienu. Ja return_tree=True, atgriež (move, root_tree).
    """
    if stats is None:
        stats = SearchStats()

    moves = legal_moves(state)
    if not moves:
        raise ValueError("No legal moves available.")

    t0 = time.perf_counter()

    root = build_tree(state, depth, stats=stats)

    algo = algorithm.lower()
    if algo == "minimax":
        minimax_on_tree(root, depth, maximizing_ai=True, stats=stats)
    elif algo in ("alphabeta", "alpha-beta", "alpha_beta"):
        alphabeta_on_tree(root, depth, alpha=float("-inf"), beta=float("inf"), maximizing_ai=True, stats=stats)
    else:
        raise ValueError("Unknown algorithm. Use 'minimax' or 'alphabeta'.")

    best_move = None
    best_val = float("-inf")
    for ch in root.children:
        val = ch.value if ch.value is not None else heuristic(ch.state)
        if val > best_val:
            best_val = val
            best_move = ch.move

    if best_move is None:
        best_move = moves[0]

    t1 = time.perf_counter()
    stats.total_ai_time += (t1 - t0)
    stats.ai_moves += 1

    if return_tree:
        return int(best_move), root
    return int(best_move)