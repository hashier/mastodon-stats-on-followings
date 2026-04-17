import sys
import os
from dotenv import load_dotenv
from mastodon import Mastodon
import datetime

load_dotenv()

INSTANCE_URL = os.getenv("MASTODON_INSTANCE_URL", "https://chaos.social")

LIMIT = 120
LAST_N_DAYS = 14

VERBOSE = False

mastodon: Mastodon


def fetch_pages(page, limit=None):
    data = []
    while page:
        data.extend(page)
        if limit and len(data) >= limit:
            break
        page = mastodon.fetch_next(page)
    return data


def fetch_all_following():
    first_page = mastodon.account_following(mastodon.me()["id"])
    return fetch_pages(first_page)


def fetch_statuses(account_id, limit=40):
    first_page = mastodon.account_statuses(account_id, limit=limit)
    return fetch_pages(first_page, limit=LIMIT)


def categorize_statuses(statuses, account_id):
    threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=LAST_N_DAYS
    )
    posts, threads, boosts = 0, 0, 0
    for s in statuses:
        if s["created_at"] <= threshold:
            continue
        if s["reblog"]:
            boosts += 1
        elif s["in_reply_to_id"] and s["in_reply_to_account_id"] == account_id:
            threads += 1
        elif not s["in_reply_to_id"]:
            posts += 1
    return posts, threads, boosts


def create_stats_of_followings(followings):
    stats = {}

    for i, follow in enumerate(followings):
        account_id = follow["id"]
        statuses = fetch_statuses(account_id, limit=LIMIT)
        stats[follow["username"]] = categorize_statuses(statuses, account_id)

        if VERBOSE:
            remaining = int(mastodon.ratelimit_remaining)
            limit = int(mastodon.ratelimit_limit)
            reset = datetime.datetime.fromtimestamp(
                mastodon.ratelimit_reset, tz=datetime.timezone.utc
            ).astimezone()
            print(
                f"  {i + 1:3}/{len(followings)}"
                f"  [API rate limit: {remaining}/{limit},"
                f" resets at {reset:%H:%M:%S}]"
            )

    return sorted(stats.items(), key=lambda x: sum(x[1]), reverse=True)


def print_stats(sorted_stats):
    print(f"Timeline noise for the last {LAST_N_DAYS} days (sorted by total):\n")
    if not sorted_stats:
        return
    max_name = max(len(name) for name, _ in sorted_stats)
    totals = [sum(counts) for _, counts in sorted_stats]
    max_total = len(str(max(totals)))
    for username, (posts, threads, boosts) in sorted_stats:
        total = posts + threads + boosts
        left = f"  {username} "
        dots = "." * max(3, max_name - len(username) + 3)
        right = (
            f" {posts:>3} posts"
            f"  {threads:>3} threads"
            f"  {boosts:>3} boosts"
            f"  {total:>{max_total}} total"
            f"  {total / LAST_N_DAYS:.1f}/day"
        )
        print(f"{left}{dots}{right}")


if __name__ == "__main__":
    VERBOSE = True

    if not os.getenv("MASTODON_ACCESS_TOKEN"):
        sys.exit("Please export the env var 'MASTODON_ACCESS_TOKEN'")

    mastodon = Mastodon(
        access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
        api_base_url=INSTANCE_URL,
    )

    if len(sys.argv) == 1:
        followings = fetch_all_following()
        stats = create_stats_of_followings(followings)
    elif len(sys.argv) == 2:
        account = mastodon.account_lookup(sys.argv[1])
        stats = create_stats_of_followings([account])
    else:
        sys.exit(
            f"Usage: {sys.argv[0]} without argument prints stats about all the people you follow. The 1st argument can be an account (user@server) and it will print out posting stats for that account"
        )

    print_stats(stats)
