import random
import json
import numpy as np
from rich import print
from rich.table import Table

DATA_FILE = "data.json"
WINNING_SCORE = 50

# fixed score bands (tuple)
SCORE_BANDS = (
    ("Beginner", 0, 15),
    ("Rising Star", 16, 30),
    ("Pro", 31, 49),
    ("Champion", 50, 9999),
)


# Dice class
class Dice:
    def roll(self):
        return random.randint(1, 6)


# Player class
class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.score = 0
        self.turn_history = []  # list of past turn scores

    # get performance band
    def get_band(self):
        for band_name, low, high in SCORE_BANDS:
            if low <= self.score <= high:
                return band_name
        return "Unranked"

    # convert player to dictionary for saving
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "turn_history": self.turn_history,
        }


# Game class
class Game:
    def __init__(self):
        self.players = []
        self.dice = Dice()
        self.used_names = set()  # tracks names already taken

    # get valid number of players
    def get_valid_number_of_players(self):
        while True:
            try:
                n = input("Enter number of players (2-4): ").strip()
                n = int(n)
                if n < 2 or n > 4:
                    raise ValueError
                return n
            except ValueError:
                print("[red]Invalid input. Please enter a whole number between 2 and 4.[/red]")

    # get valid player name
    def get_valid_player_name(self, default_id):
        while True:
            name = input(f"Enter name for Player {default_id}: ").strip()
            if name == "":
                print("[red]Name cannot be empty.[/red]")
                continue
            if len(name) > 15:
                print("[red]Name is too long. Use 15 characters or fewer.[/red]")
                continue
            if name in self.used_names:
                print("[red]That name is already taken. Choose another.[/red]")
                continue
            self.used_names.add(name)
            return name

    # create players
    def create_players(self):
        n = self.get_valid_number_of_players()
        self.players = []
        self.used_names = set()
        for i in range(n):
            name = self.get_valid_player_name(i + 1)
            self.players.append(Player(i + 1, name))

    # show score board
    def show_scores(self):
        table = Table(title="Score Board")
        table.add_column("Player")
        table.add_column("Score")
        table.add_column("Band")

        for p in self.players:
            table.add_row(p.name, str(p.score), p.get_band())

        print(table)

    # show statistics using numpy
    def show_statistics(self):
        all_turns = []
        for p in self.players:
            all_turns.extend(p.turn_history)

        if not all_turns:
            print("[yellow]No turns played yet, no statistics available.[/yellow]")
            return

        arr = np.array(all_turns)

        table = Table(title="Game Statistics (NumPy)")
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Total turns played", str(arr.size))
        table.add_row("Average turn score", f"{np.mean(arr):.2f}")
        table.add_row("Highest turn score", str(np.max(arr)))
        table.add_row("Lowest turn score", str(np.min(arr)))
        table.add_row("Std deviation", f"{np.std(arr):.2f}")
        print(table)

        for p in self.players:
            if p.turn_history:
                avg = np.mean(np.array(p.turn_history))
                print(f"[cyan]{p.name}[/cyan]: average turn score = {avg:.2f}")

    # save game
    def save_game(self):
        try:
            data = [p.to_dict() for p in self.players]
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print("[green]Game Saved[/green]")
        except OSError as e:
            print(f"[red]Could not save game: {e}[/red]")

    # load game
    def load_game(self):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            if not data:
                raise ValueError("Save file is empty.")

            self.players = []
            self.used_names = set()
            for item in data:
                p = Player(item["id"], item["name"])
                p.score = item.get("score", 0)
                p.turn_history = item.get("turn_history", [])
                self.players.append(p)
                self.used_names.add(p.name)

            print("[green]Game Loaded[/green]")
            return True

        except FileNotFoundError:
            print("[yellow]No saved game found. Starting fresh.[/yellow]")
            return False
        except (json.JSONDecodeError, ValueError, KeyError):
            print("[red]Saved file is corrupted or invalid. Starting fresh.[/red]")
            return False

    # player turn
    def play_turn(self, player):
        print(f"\n[bold yellow]{player.name}'s Turn[/bold yellow]")
        print(f"Current Score: {player.score}")

        temp = 0

        while True:
            choice = input("Roll? (y/n): ").strip().lower()

            if choice not in ("y", "n"):
                print("[red]Invalid choice, please enter 'y' or 'n'.[/red]")
                continue

            if choice == "n":
                break

            val = self.dice.roll()
            print(f"[cyan]Dice: {val}[/cyan]")

            if val == 1:
                print("[red]Rolled a 1. Turn score lost![/red]")
                temp = 0
                break
            else:
                temp += val

            print(f"Turn score so far: {temp}")

        player.score += temp
        player.turn_history.append(temp)
        print(f"Total score: {player.score}")

    # check winner
    def check_winner(self):
        for p in self.players:
            if p.score >= WINNING_SCORE:
                return p
        return None

    # start game
    def start(self):
        print("[bold green]Welcome to Pig Dice Game[/bold green]")

        choice = input("Load saved game? (y/n): ").strip().lower()

        if choice == "y":
            loaded = self.load_game()
            if not loaded:
                self.create_players()
        else:
            self.create_players()

        while True:
            for p in self.players:
                self.play_turn(p)
                self.save_game()
                self.show_scores()

                winner = self.check_winner()
                if winner:
                    print(f"\n[bold green]Winner: {winner.name}[/bold green]")
                    print(f"Score: {winner.score}")
                    self.show_statistics()
                    return


# run game
g = Game()
g.start()