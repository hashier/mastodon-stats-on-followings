# mastodon-stats-on-followings

Find out which of the people you follow on Mastodon are the most chatty.

Shows post counts (excluding replies) for the last 14 days, sorted by activity.

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
Posts that were not replies of the last 14 days:
alice: 42 posts. Average 3.000 a day.
bob: 17 posts. Average 1.214 a day.
carol: 3 posts. Average 0.214 a day.
```

## Configuration

These constants at the top of `masto.py` can be adjusted:

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
