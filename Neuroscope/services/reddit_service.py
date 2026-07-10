from utils.reddit_fetcher import (
    fetch_reddit_comments,
    fetch_reddit_post_metadata
)


def fetch_reddit_discussion(reddit_url, comment_limit=100, include_replies=False):
    metadata = fetch_reddit_post_metadata(reddit_url)
    comments = fetch_reddit_comments(
        reddit_url,
        limit=comment_limit,
        include_replies=include_replies
    )
    return metadata, comments