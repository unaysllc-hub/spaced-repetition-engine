from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True, slots=True)
class CardState:
    card_id: str
    due: date
    interval_days: int = 0
    repetitions: int = 0
    ease_factor: float = 2.5
    lapses: int = 0

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["due"] = self.due.isoformat()
        return value

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "CardState":
        return cls(
            card_id=str(value["card_id"]),
            due=date.fromisoformat(str(value["due"])),
            interval_days=int(value.get("interval_days", 0)),
            repetitions=int(value.get("repetitions", 0)),
            ease_factor=float(value.get("ease_factor", 2.5)),
            lapses=int(value.get("lapses", 0)),
        )


@dataclass(frozen=True, slots=True)
class ReviewResult:
    previous: CardState
    current: CardState
    quality: int


def review(state: CardState, quality: int, reviewed_on: date | None = None) -> ReviewResult:
    """Apply an SM-2-style review where quality ranges from 0 to 5."""
    if not 0 <= quality <= 5:
        raise ValueError("quality must be between 0 and 5")
    reviewed_on = reviewed_on or date.today()

    ease = max(
        1.3,
        state.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    if quality < 3:
        interval = 1
        repetitions = 0
        lapses = state.lapses + 1
    else:
        repetitions = state.repetitions + 1
        lapses = state.lapses
        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = max(1, round(state.interval_days * ease))

    current = CardState(
        card_id=state.card_id,
        due=reviewed_on + timedelta(days=interval),
        interval_days=interval,
        repetitions=repetitions,
        ease_factor=round(ease, 4),
        lapses=lapses,
    )
    return ReviewResult(previous=state, current=current, quality=quality)


def due_cards(cards: Iterable[CardState], on_date: date | None = None) -> list[CardState]:
    """Return due cards, with overdue and frequently lapsed cards first."""
    on_date = on_date or date.today()
    return sorted(
        (card for card in cards if card.due <= on_date),
        key=lambda card: (card.due, -card.lapses, card.card_id),
    )
