# mastodon-stats-on-followings

Find out which of the people you follow on Mastodon are the most chatty.

Shows timeline noise (posts, self-threads, and boosts) for the last 14 days, sorted by total activity. Helps you find accounts that flood your timeline so you can curate who you follow.

## Setup

```sh
uv venv
uv pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your values. You need a Mastodon access token with `read` scope — create one in your instance under Preferences > Development > New Application.

## Usage

Stats for everyone you follow:

```sh
python masto.py
```

Stats for a specific account:

```sh
python masto.py user@instance.social
```

## Example output

```
Timeline noise for the last 14 days (sorted by total):

  alice ..   21 posts    5 threads   12 boosts  38 total  2.7/day
  bob ....    3 posts    0 threads   30 boosts  33 total  2.4/day
  carol ..   18 posts    3 threads    0 boosts  21 total  1.5/day
```

## Configuration

Set these in `.env`:

| Variable | Default | Description |
|---|---|---|
| `MASTODON_ACCESS_TOKEN` | (required) | Your Mastodon access token |
| `MASTODON_INSTANCE_URL` | `https://chaos.social` | Your Mastodon instance |

These constants in `masto.py` can also be adjusted:

| Constant | Default | Description |
|---|---|---|
| `LIMIT` | `120` | Max statuses fetched per account. If someone posted more than this in the time window, their count will be undercounted. |
| `LAST_N_DAYS` | `14` | Time window for counting posts |

## Rate limits

The Mastodon API allows 300 requests per 5 minutes. The script makes one request per ~40 statuses per account, so fetching stats for 200+ followings may take a while. Progress is printed to stdout.

## License

MIT
