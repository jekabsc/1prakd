# gui_app.py
from __future__ import annotations

import random
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from typing import List

from engine import GameState, legal_moves, apply_move, is_terminal, final_result
from ai_player import choose_move, save_tree_txt


def generate_start_numbers(k: int = 5, low: int = 40000, high: int = 50000) -> List[int]:
    result = set()
    while len(result) < k:
        x = random.randint(low, high)
        x -= x % 60  # dalās ar 3,4,5 -> dalās ar 60
        if low <= x <= high and x % 60 == 0:
            result.add(x)
    return sorted(result)


class GameGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Dalīšanas spēle (3/4/5) — Cilvēks vs AI")
        self.root.geometry("760x500")
        self.root.minsize(760, 500)

        self.state: GameState | None = None
        self.start_n: int | None = None

        self.results: List[dict] = []
        self.algorithm = tk.StringVar(value="alphabeta")
        self.depth = tk.IntVar(value=6)
        self.starter = tk.StringVar(value="human")  # human/ai

        tk.Label(root, text="Dalīšanas spēle: dalīt ar 3 / 4 / 5", font=("Arial", 16, "bold")).pack(pady=10)

        main = tk.Frame(root)
        main.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right = tk.Frame(main)
        right.pack(side="right", fill="y")

        # Start numbers
        tk.Label(left, text="1) Izvēlies sākuma skaitli:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.start_list = tk.Listbox(left, height=6, font=("Consolas", 12))
        self.start_list.pack(fill="x", pady=6)

        btnrow = tk.Frame(left)
        btnrow.pack(anchor="w", pady=(0, 6))
        tk.Button(btnrow, text="Ģenerēt 5 skaitļus", command=self.on_generate).pack(side="left", padx=(0, 6))
        tk.Button(btnrow, text="Sākt ar izvēlēto", command=self.on_start).pack(side="left")

        # AI settings
        tk.Label(left, text="2) Datora iestatījumi:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(12, 0))

        algrow = tk.Frame(left)
        algrow.pack(anchor="w", pady=4)
        tk.Label(algrow, text="Algoritms:").pack(side="left")
        tk.Radiobutton(algrow, text="Minimax", variable=self.algorithm, value="minimax").pack(side="left", padx=6)
        tk.Radiobutton(algrow, text="Alfa-beta", variable=self.algorithm, value="alphabeta").pack(side="left", padx=6)

        drow = tk.Frame(left)
        drow.pack(anchor="w", pady=4)
        tk.Label(drow, text="Dziļums:").pack(side="left")
        tk.Spinbox(drow, from_=1, to=12, textvariable=self.depth, width=5).pack(side="left", padx=6)

        tk.Label(left, text="Kurš sāk?", font=("Arial", 11, "bold")).pack(anchor="w", pady=(6, 0))
        srow = tk.Frame(left)
        srow.pack(anchor="w", pady=4)
        tk.Radiobutton(srow, text="Cilvēks", variable=self.starter, value="human").pack(side="left", padx=6)
        tk.Radiobutton(srow, text="Dators", variable=self.starter, value="ai").pack(side="left", padx=6)

        # Status
        tk.Label(left, text="3) Spēles stāvoklis:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(12, 0))

        self.status = tk.StringVar(value="Spied “Ģenerēt 5 skaitļus”, izvēlies un sāc.")
        tk.Label(left, textvariable=self.status, anchor="w", justify="left").pack(fill="x", pady=6)

        self.n_var = tk.StringVar(value="-")
        self.score_var = tk.StringVar(value="-")
        self.bank_var = tk.StringVar(value="-")
        self.turn_var = tk.StringVar(value="-")
        self.moves_var = tk.StringVar(value="-")

        self._kv(left, "Skaitlis:", self.n_var)
        self._kv(left, "Punkti:", self.score_var)
        self._kv(left, "Banka:", self.bank_var)
        self._kv(left, "Gājiens:", self.turn_var)
        self._kv(left, "Dalītāji:", self.moves_var)

        # Right panel: move buttons
        tk.Label(right, text="Gājiens", font=("Arial", 12, "bold")).pack(pady=(0, 8))

        self.btn3 = tk.Button(right, text="Dalīt ar 3", width=20, command=lambda: self.on_human_move(3))
        self.btn4 = tk.Button(right, text="Dalīt ar 4", width=20, command=lambda: self.on_human_move(4))
        self.btn5 = tk.Button(right, text="Dalīt ar 5", width=20, command=lambda: self.on_human_move(5))
        self.btn3.pack(pady=4)
        self.btn4.pack(pady=4)
        self.btn5.pack(pady=4)

        tk.Button(right, text="Reset", width=20, command=self.on_reset).pack(pady=(14, 6))

        # Tree save button
        tk.Button(right, text="Saglabāt koku (TXT)", width=20, command=self.save_tree_button).pack(pady=(0, 10))

        # Results history + save CSV
        tk.Label(right, text="Rezultātu vēsture", font=("Arial", 11, "bold")).pack(pady=(4, 6))
        self.results_list = tk.Listbox(right, height=8, width=32, font=("Consolas", 10))
        self.results_list.pack(pady=(0, 6))

        tk.Button(right, text="Saglabāt rezultātus (CSV)", width=20, command=self.save_results).pack(pady=(0, 6))
        tk.Button(right, text="Notīrīt vēsturi", width=20, command=self.clear_results).pack()

        self._set_move_buttons(False)
        self.on_generate()

    def _kv(self, parent: tk.Widget, k: str, v: tk.StringVar) -> None:
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=k, width=12, anchor="w").pack(side="left")
        tk.Label(row, textvariable=v, anchor="w", font=("Consolas", 11)).pack(side="left")

    def _set_move_buttons(self, enabled: bool) -> None:
        s = tk.NORMAL if enabled else tk.DISABLED
        self.btn3.config(state=s)
        self.btn4.config(state=s)
        self.btn5.config(state=s)

    def _refresh(self) -> None:
        if self.state is None:
            self.n_var.set("-")
            self.score_var.set("-")
            self.bank_var.set("-")
            self.turn_var.set("-")
            self.moves_var.set("-")
            self._set_move_buttons(False)
            return

        moves = legal_moves(self.state)
        self.n_var.set(str(self.state.n))
        self.score_var.set(str(self.state.score))
        self.bank_var.set(str(self.state.bank))
        self.turn_var.set("Cilvēks" if self.state.turn == 0 else "Dators")
        self.moves_var.set(", ".join(map(str, moves)) if moves else "nav")

        if self.state.turn == 0 and moves:
            self._set_move_buttons(True)
            self.btn3.config(state=(tk.NORMAL if 3 in moves else tk.DISABLED))
            self.btn4.config(state=(tk.NORMAL if 4 in moves else tk.DISABLED))
            self.btn5.config(state=(tk.NORMAL if 5 in moves else tk.DISABLED))
        else:
            self._set_move_buttons(False)

    def on_generate(self) -> None:
        self.start_list.delete(0, tk.END)
        for x in generate_start_numbers():
            self.start_list.insert(tk.END, str(x))
        self.state = None
        self.start_n = None
        self.status.set("Izvēlies sākuma skaitli un spied “Sākt ar izvēlēto”.")
        self._refresh()

    def on_start(self) -> None:
        sel = self.start_list.curselection()
        if not sel:
            messagebox.showwarning("Nav izvēles", "Izvēlies vienu sākuma skaitli sarakstā.")
            return

        start_n = int(self.start_list.get(sel[0]))
        self.start_n = start_n
        turn = 0 if self.starter.get() == "human" else 1
        self.state = GameState(n=start_n, score=0, bank=0, turn=turn)

        self._refresh()

        if self.state.turn == 1 and not is_terminal(self.state):
            self.status.set("Spēle sākta. Sāk dators…")
            self.root.after(200, self.do_ai)
        else:
            self.status.set("Spēle sākta. Tavs gājiens.")

    def on_human_move(self, move: int) -> None:
        if self.state is None or self.state.turn != 0:
            return
        if move not in legal_moves(self.state):
            messagebox.showerror("Nederīgs gājiens", "Šobrīd ar šo dalītāju dalīt nedrīkst.")
            return

        self.state = apply_move(self.state, move)
        self.status.set(f"Tu: dalīt ar {move}.")
        self._refresh()

        if self.state and is_terminal(self.state):
            self.finish()
            return

        self.root.after(200, self.do_ai)

    def do_ai(self) -> None:
        if self.state is None or self.state.turn != 1:
            return

        moves = legal_moves(self.state)
        if not moves:
            self.finish()
            return

        alg = self.algorithm.get()
        depth = int(self.depth.get())

        try:
            ai_move, tree = choose_move(self.state, algorithm=alg, depth=depth, return_tree=True)
        except Exception as e:
            messagebox.showerror("AI kļūda", f"AI noplīsa: {e}\nTiks izmantots pirmais legālais gājiens.")
            ai_move = moves[0]
            tree = None

        if ai_move not in moves:
            ai_move = moves[0]

        # Automātiski saglabā pēdējo koku pēc katra AI gājiena
        if tree is not None:
            save_tree_txt(tree, filename="last_game_tree.txt", max_depth=depth)

        self.state = apply_move(self.state, ai_move)
        self.status.set(f"Dators: dalīt ar {ai_move}.")
        self._refresh()

        if self.state and is_terminal(self.state):
            self.finish()

    def finish(self) -> None:
        if self.state is None:
            return
        r = final_result(self.state)

        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "start_n": self.start_n,
            "raw_score": r["raw_score"],
            "bank": r["bank"],
            "final_score": r["final_score"],
            "winner": r["winner"],
            "algorithm": self.algorithm.get(),
            "depth": int(self.depth.get()),
            "starter": self.starter.get(),
        }
        self.results.append(entry)

        line = f"{entry['start_n']} | F:{entry['final_score']} | B:{entry['bank']} | {entry['winner']}"
        self.results_list.insert(tk.END, line)

        self._set_move_buttons(False)

        messagebox.showinfo(
            "Spēle beigusies",
            "Spēle beigusies ✅\n\n"
            f"Punkti (pirms bankas): {entry['raw_score']}\n"
            f"Banka: {entry['bank']}\n"
            f"Gala punkti: {entry['final_score']}\n"
            f"Uzvarētājs: {entry['winner']}"
        )
        self.status.set("Spēle beigusies. Spied “Ģenerēt 5 skaitļus”, lai sāktu no jauna.")

    def on_reset(self) -> None:
        self.state = None
        self.start_n = None
        self.status.set("Reset. Izvēlies sākuma skaitli un sāc.")
        self._refresh()

    # --- Tree save button (manual) ---
    def save_tree_button(self) -> None:
        if self.state is None:
            messagebox.showwarning("Nav spēles", "Vispirms sāc spēli.")
            return

        alg = self.algorithm.get()
        depth = int(self.depth.get())

        try:
            _, tree = choose_move(self.state, algorithm=alg, depth=depth, return_tree=True)
            fname = f"game_tree_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            save_tree_txt(tree, filename=fname, max_depth=depth)
            messagebox.showinfo("Saglabāts", f"Koks saglabāts:\n{fname}")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās saglabāt koku: {e}")

    # --- Results: CSV + clear ---
    def clear_results(self) -> None:
        self.results.clear()
        self.results_list.delete(0, tk.END)
        messagebox.showinfo("OK", "Rezultātu vēsture notīrīta.")

    def save_results(self) -> None:
        if not self.results:
            messagebox.showwarning("Nav ko saglabāt", "Nav neviena pabeigta spēle, ko saglabāt.")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"game_results_{ts}.csv"
        fieldnames = ["timestamp", "start_n", "raw_score", "bank", "final_score", "winner", "algorithm", "depth", "starter"]

        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(self.results)
            messagebox.showinfo("Saglabāts", f"Rezultāti saglabāti failā:\n{filename}")
        except Exception as e:
            messagebox.showerror("Kļūda", f"Neizdevās saglabāt: {e}")


def main() -> None:
    root = tk.Tk()
    GameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()