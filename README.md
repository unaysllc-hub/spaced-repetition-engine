# Spaced Repetition Engine

A dependency-free Python scheduling engine and command-line tool for local flashcard systems. It uses an SM-2-style algorithm, stores portable JSON, prioritizes overdue cards, and never sends study data to a server.

## Install

```bash
python -m pip install .
```

## Use

```bash
spaced-review --state biology.json add cell-membrane
spaced-review --state biology.json due
spaced-review --state biology.json review cell-membrane 4
spaced-review --state biology.json list
```

Review quality ranges from `0` (complete blackout) to `5` (perfect response). A score below `3` records a lapse and schedules a short relearning interval.

## Library example

```python
from datetime import date
from spaced_repetition_engine import CardState, review

card = CardState("albanian-vocabulary-01", due=date.today())
next_state = review(card, quality=4).current
print(next_state.due, next_state.interval_days)
```

## Test

```bash
python -m unittest discover -s tests -v
```

The algorithm is an educational scheduling foundation, not a clinical memory assessment.

## License

MIT License.
