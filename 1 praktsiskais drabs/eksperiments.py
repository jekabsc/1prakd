# experiments.py
from __future__ import annotations

import random
import csv
from datetime import datetime
from typing import List, Dict, Any

from engine import GameState, legal_moves, apply_move, is_terminal, final_result
from ai_player import choose_move, SearchStats


def generate_start_numbers(k: int = 5, low: int = 40000, high: int = 50000) -> List[int]:
    # dalās ar 3,4,5 -> dalās ar 60
    result = set()
    while len(result) < k:
        x = random.randint(low, high)
        x -= x % 60
        if low <= x <= high and x % 60 == 0:
            result.add(x)
    return sorted(result)


def human_policy_random(state: GameState) -> int:
    """Eksperimentiem: cilvēks = random legāls gājiens."""
    return random.choice(legal_moves(state))


def play_one_game(algorithm: str, depth: int, starter: str = "human") -> Dict[str, Any]:
    stats = SearchStats()

    start_n = random.choice(generate_start_numbers())
    turn = 0 if starter == "human" else 1
    state = GameState(n=start_n, score=0, bank=0, turn=turn)

    while not is_terminal(state):
        if state.turn == 0:
            m = human_policy_random(state)
            state = apply_move(state, m)
        else:
            m = choose_move(state, algorithm=algorithm, depth=depth, stats=stats)
            state = apply_move(state, m)

    r = final_result(state)

    return {
        "start_n": start_n,
        "winner": r["winner"],
        "winner_is_ai": bool(r.get("winner_is_ai", False)),
        "generated_nodes_total": int(stats.generated_nodes),
        "evaluated_nodes_total": int(stats.evaluated_nodes),
        "ai_moves": int(stats.ai_moves),
        "avg_ai_move_time_s": float(stats.avg_ai_move_time),
    }


def run_experiments(algorithm: str, n: int, depth: int, starter: str) -> Dict[str, Any]:
    ai_wins = 0
    human_wins = 0

    gen_sum = 0
    eval_sum = 0
    avg_time_sum = 0.0
    ai_moves_sum = 0

    games: List[Dict[str, Any]] = []

    for _ in range(n):
        res = play_one_game(algorithm=algorithm, depth=depth, starter=starter)
        games.append(res)

        if res["winner_is_ai"]:
            ai_wins += 1
        else:
            human_wins += 1

        gen_sum += res["generated_nodes_total"]
        eval_sum += res["evaluated_nodes_total"]
        avg_time_sum += res["avg_ai_move_time_s"]
        ai_moves_sum += res["ai_moves"]

    return {
        "algorithm": algorithm,
        "n_games": n,
        "depth": depth,
        "starter": starter,
        "ai_wins": ai_wins,
        "human_wins": human_wins,
        "generated_nodes_total_all_games": gen_sum,
        "evaluated_nodes_total_all_games": eval_sum,
        "avg_ai_move_time_s_avg_per_game": (avg_time_sum / n) if n else 0.0,
        "generated_nodes_avg_per_game": (gen_sum / n) if n else 0.0,
        "evaluated_nodes_avg_per_game": (eval_sum / n) if n else 0.0,
        "ai_moves_total_all_games": ai_moves_sum,
        "per_game": games,
    }


def write_csv(all_runs: List[Dict[str, Any]], filename: str) -> None:
    """
    CSV satur gan katras spēles rindas, gan kopsavilkuma rindas.
    """
    fieldnames = [
        "timestamp",
        "algorithm",
        "depth",
        "starter",
        "game_index",
        "start_n",
        "winner",
        "winner_is_ai",
        "generated_nodes_total",
        "evaluated_nodes_total",
        "ai_moves",
        "avg_ai_move_time_s",
        "run_ai_wins",
        "run_human_wins",
        "run_generated_nodes_total_all_games",
        "run_evaluated_nodes_total_all_games",
        "run_avg_ai_move_time_s_avg_per_game",
    ]

    ts = datetime.now().isoformat(timespec="seconds")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()

        for run in all_runs:
            # per-game rows
            for idx, g in enumerate(run["per_game"], start=1):
                w.writerow({
                    "timestamp": ts,
                    "algorithm": run["algorithm"],
                    "depth": run["depth"],
                    "starter": run["starter"],
                    "game_index": idx,
                    "start_n": g["start_n"],
                    "winner": g["winner"],
                    "winner_is_ai": g["winner_is_ai"],
                    "generated_nodes_total": g["generated_nodes_total"],
                    "evaluated_nodes_total": g["evaluated_nodes_total"],
                    "ai_moves": g["ai_moves"],
                    "avg_ai_move_time_s": f"{g['avg_ai_move_time_s']:.6f}",
                    "run_ai_wins": run["ai_wins"],
                    "run_human_wins": run["human_wins"],
                    "run_generated_nodes_total_all_games": run["generated_nodes_total_all_games"],
                    "run_evaluated_nodes_total_all_games": run["evaluated_nodes_total_all_games"],
                    "run_avg_ai_move_time_s_avg_per_game": f"{run['avg_ai_move_time_s_avg_per_game']:.6f}",
                })


def write_summary_txt(all_runs: List[Dict[str, Any]], filename: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append(f"EXPERIMENT SUMMARY ({ts})")
    lines.append("=" * 72)

    for run in all_runs:
        lines.append(f"ALGORITHM: {run['algorithm'].upper()} | games={run['n_games']} | depth={run['depth']} | starter={run['starter']}")
        lines.append(f"AI wins: {run['ai_wins']} | Human wins: {run['human_wins']}")
        lines.append(f"Generated vertices (TOTAL): {run['generated_nodes_total_all_games']}")
        lines.append(f"Evaluated vertices (TOTAL): {run['evaluated_nodes_total_all_games']}")
        lines.append(f"Avg AI move time (seconds, AVG per game): {run['avg_ai_move_time_s_avg_per_game']:.6f}")
        lines.append("-" * 72)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    # Parametri
    N = 10
    DEPTH = 6
    STARTER = "human"  # "human" vai "ai"

    runs = [
        run_experiments("minimax", n=N, depth=DEPTH, starter=STARTER),
        run_experiments("alphabeta", n=N, depth=DEPTH, starter=STARTER),
    ]

    write_csv(runs, "experiments_results.csv")
    write_summary_txt(runs, "experiments_summary.txt")

    # Minimāla ziņa (ja gribi, vari arī izdzēst šo print)
    print("Saved: experiments_results.csv, experiments_summary.txt")


if __name__ == "__main__":
    main()