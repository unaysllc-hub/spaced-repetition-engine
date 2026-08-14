from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .engine import CardState, due_cards, review


def load(path: Path) -> dict[str, CardState]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["card_id"]: CardState.from_dict(item) for item in data.get("cards", [])}


def save(path: Path, cards: dict[str, CardState]) -> None:
    payload = {"version": 1, "cards": [card.to_dict() for card in sorted(cards.values(), key=lambda item: item.card_id)]}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Local spaced-repetition scheduling engine")
    root.add_argument("--state", type=Path, default=Path("cards.json"), help="JSON state file")
    commands = root.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Add a new card")
    add.add_argument("card_id")
    review_command = commands.add_parser("review", help="Record a review quality from 0 to 5")
    review_command.add_argument("card_id")
    review_command.add_argument("quality", type=int, choices=range(6))
    commands.add_parser("due", help="List cards due today")
    commands.add_parser("list", help="List all card states")
    return root


def main() -> int:
    args = parser().parse_args()
    cards = load(args.state)
    if args.command == "add":
        if args.card_id in cards:
            raise SystemExit(f"Card already exists: {args.card_id}")
        cards[args.card_id] = CardState(args.card_id, date.today())
        save(args.state, cards)
        print(f"Added {args.card_id}; it is due now.")
    elif args.command == "review":
        if args.card_id not in cards:
            raise SystemExit(f"Unknown card: {args.card_id}")
        result = review(cards[args.card_id], args.quality)
        cards[args.card_id] = result.current
        save(args.state, cards)
        print(f"Next review: {result.current.due.isoformat()} ({result.current.interval_days} day interval)")
    else:
        selected = due_cards(cards.values()) if args.command == "due" else sorted(cards.values(), key=lambda item: item.card_id)
        for card in selected:
            print(f"{card.card_id}\tdue={card.due.isoformat()}\tinterval={card.interval_days}\tease={card.ease_factor:.2f}\tlapses={card.lapses}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
