import datetime

import pytest
from mastodon.errors import MastodonNetworkError

import masto

NOW = datetime.datetime.now(datetime.timezone.utc)


def status(days_ago=0, reblog=None, in_reply_to_id=None, in_reply_to_account_id=None):
    return {
        "created_at": NOW - datetime.timedelta(days=days_ago),
        "reblog": reblog,
        "in_reply_to_id": in_reply_to_id,
        "in_reply_to_account_id": in_reply_to_account_id,
    }


class FakeMastodon:
    """Serves canned statuses; account_statuses fails `failures[id]` times first."""

    def __init__(self, statuses=None, failures=None):
        self.statuses = statuses or {}
        self.failures = dict(failures or {})
        self.calls = {}

    def account_statuses(self, account_id, limit=40):
        self.calls[account_id] = self.calls.get(account_id, 0) + 1
        if self.failures.get(account_id, 0) > 0:
            self.failures[account_id] -= 1
            raise MastodonNetworkError("Could not complete request: Read timed out.")
        return list(self.statuses.get(account_id, [status()]))

    def fetch_next(self, page):
        return None


@pytest.fixture
def install_fake(monkeypatch):
    def _install(fake):
        monkeypatch.setattr(masto, "mastodon", fake, raising=False)
        monkeypatch.setattr(masto.time, "sleep", lambda seconds: None)
        return fake

    return _install


def test_categorize_splits_posts_threads_boosts():
    account_id = 42
    statuses = [
        status(),
        status(reblog={"id": 1}),
        status(in_reply_to_id=7, in_reply_to_account_id=account_id),
    ]
    assert masto.categorize_statuses(statuses, account_id) == (1, 1, 1)


def test_categorize_ignores_replies_to_others():
    statuses = [status(in_reply_to_id=7, in_reply_to_account_id=99)]
    assert masto.categorize_statuses(statuses, 42) == (0, 0, 0)


def test_categorize_ignores_statuses_older_than_window():
    statuses = [status(days_ago=masto.LAST_N_DAYS + 1)]
    assert masto.categorize_statuses(statuses, 42) == (0, 0, 0)


def test_transient_network_failure_is_retried(install_fake):
    fake = install_fake(FakeMastodon(failures={1: 1}))
    stats = masto.create_stats_of_followings(
        [{"id": 1, "username": "flaky"}, {"id": 2, "username": "fine"}]
    )
    assert sorted(name for name, _ in stats) == ["fine", "flaky"]
    assert fake.calls[1] == 2


def test_persistent_network_failure_skips_account(install_fake):
    install_fake(FakeMastodon(failures={1: 999}))
    stats = masto.create_stats_of_followings(
        [{"id": 1, "username": "dead"}, {"id": 2, "username": "fine"}]
    )
    assert [name for name, _ in stats] == ["fine"]


def test_retry_attempts_are_bounded(install_fake):
    fake = install_fake(FakeMastodon(failures={1: 999}))
    masto.create_stats_of_followings([{"id": 1, "username": "dead"}])
    assert fake.calls[1] == len(masto.RETRY_WAITS) + 1


def test_stats_sorted_by_total_descending(install_fake):
    install_fake(
        FakeMastodon(
            statuses={
                1: [status()],
                2: [status(), status(reblog={"id": 1})],
            }
        )
    )
    stats = masto.create_stats_of_followings(
        [{"id": 1, "username": "quiet"}, {"id": 2, "username": "loud"}]
    )
    assert [name for name, _ in stats] == ["loud", "quiet"]
