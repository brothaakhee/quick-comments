# quick-comments

A comment API using DRF that allows users to submit comments associated with a
content URL and list comments per content.

# Endpoint example usage:

`GET /content/`

See a list of content

`GET /content/<slug>/`

See the details for a particular instance of content along with all comments
associated with it

`GET /comments/`

See all comments

```
POST /comments/
{
    "username": "myuser",
    "content_url": "some-url",
    "comment": "this is my first comment"
}
```

Will create a comment for the content URL "some-url". If that content does not
already exist, it will be created automatically.

# Throttling

The API will by default throttle:

- Any user that makes more than 20 requests per minute.
- Any user that tries to post more than 2 comments in a minute.
- Any user that tries to post a comment that exactly matches a comment posted
  within the last 24 hours.

## Configuration

The defaults for the throttling can be changed by setting env variables and
changing the defaults to the values you desire.

```
EXCESS_COMMENTS_LOCKOUT=300
EXCESS_COMMENTS_RATE=2/minute

DUPLICATE_COMMENT_LOCKOUT=60
DUPLICATE_COMMENT_HOURS=24

DEFAULT_ANON_THROTTLE_RATE=20/minute
DEFAULT_USER_THROTTLE_RATE=20/minute
```
