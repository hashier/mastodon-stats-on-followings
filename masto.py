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
    data = list(page)
    while page := mastodon.fetch_next(page):
        data.extend(page)
        if limit and len(data) >= limit:
            break
    return data


def fetch_all_following():
    first_page = mastodon.account_following(mastodon.me()["id"])
    return fetch_pages(first_page)


def fetch_statuses(account_id, limit=40):
    first_page = mastodon.account_statuses(account_id, limit=limit)
    return fetch_pages(first_page, limit=LIMIT)


def create_stats_of_followings(followings):
    post_counts = {}

    for i, follow in enumerate(followings):
        account_id = follow["id"]
        statuses = fetch_statuses(account_id, limit=LIMIT)

        threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=LAST_N_DAYS
        )
        recent_posts = [
            s
            for s in statuses
            if s["created_at"] > threshold and not s["in_reply_to_id"]
        ]
        post_counts[follow["username"]] = len(recent_posts)

        if VERBOSE:
            print(
                f"Done: {i + 1:3}/{len(followings)}",
                f"Limit: {mastodon.ratelimit_remaining:3} / {mastodon.ratelimit_limit}",
                f"Lastcall: {datetime.datetime.fromtimestamp(mastodon.ratelimit_lastcall, tz=datetime.timezone.utc).astimezone()}",
                f"Reset: {datetime.datetime.fromtimestamp(mastodon.ratelimit_reset, tz=datetime.timezone.utc).astimezone()}",
            )

    sorted_post_counts = sorted(post_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_post_counts


def print_stats(sorted_post_counts):
    print(f"Posts that were not replies of the last {LAST_N_DAYS} days:")
    for username, count in sorted_post_counts:
        print(f"{username}: {count} posts. Average {count / LAST_N_DAYS:.3f} a day.")


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
