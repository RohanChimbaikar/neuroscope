from utils.reddit_fetcher import (
    fetch_reddit_comments
)

comments = fetch_reddit_comments(

    "https://www.reddit.com/r/popheads/comments/1sy3xsr/ariana_grande_announces_eighth_studio_album_petal/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button"
)

print(comments[:5])