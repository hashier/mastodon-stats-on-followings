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
$ python masto.py
    1/215  [API rate limit: 292/300, resets at 16:20:01]
...
  212/215  [API rate limit: 246/300, resets at 16:35:00]
  213/215  [API rate limit: 243/300, resets at 16:35:00]
  214/215  [API rate limit: 240/300, resets at 16:35:01]
  215/215  [API rate limit: 237/300, resets at 16:35:00]
Timeline noise for the last 14 days (sorted by total):

  vncresolver ........ 120 posts    0 threads    0 boosts  120 total  8.6/day
  briankrebs .........  11 posts    3 threads   82 boosts   96 total  6.9/day
  stroughtonsmith ....  48 posts   13 threads   30 boosts   91 total  6.5/day
  siguza .............   2 posts    0 threads   80 boosts   82 total  5.9/day
  sundogplanets ......  30 posts   21 threads   25 boosts   76 total  5.4/day
  Viss ...............  10 posts    3 threads   47 boosts   60 total  4.3/day
...
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
