import unittest
from datetime import date, timedelta

from spaced_repetition_engine import CardState, due_cards, review


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 8, 14)
        self.card = CardState("biology-cell", self.today)

    def test_successful_reviews_grow_intervals(self):
        first = review(self.card, 5, self.today).current
        second = review(first, 5, first.due).current
        third = review(second, 5, second.due).current
        self.assertEqual((first.interval_days, second.interval_days), (1, 6))
        self.assertGreater(third.interval_days, second.interval_days)

    def test_failed_review_resets_repetitions_and_records_lapse(self):
        learned = review(review(self.card, 4, self.today).current, 4, self.today + timedelta(days=1)).current
        failed = review(learned, 1, learned.due).current
        self.assertEqual(failed.repetitions, 0)
        self.assertEqual(failed.interval_days, 1)
        self.assertEqual(failed.lapses, 1)

    def test_quality_is_validated(self):
        with self.assertRaises(ValueError):
            review(self.card, 6, self.today)

    def test_due_cards_excludes_future_items_and_orders_overdue_first(self):
        cards = [
            CardState("future", self.today + timedelta(days=1)),
            CardState("today", self.today),
            CardState("overdue", self.today - timedelta(days=3)),
        ]
        self.assertEqual([card.card_id for card in due_cards(cards, self.today)], ["overdue", "today"])


if __name__ == "__main__":
    unittest.main()
