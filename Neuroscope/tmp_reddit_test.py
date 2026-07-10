import requests
from urllib.parse import urlparse, urlunparse

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.reddit.com/',
    'Connection': 'keep-alive',
}

urls = [
    'https://www.reddit.com/r/Python/comments/15xpn7t/whats_everyone_working-on-this-weekend/',
]

for u in urls:
    parsed = urlparse(u)
    base = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip('/'), '', '', ''))
    targets = [
        base + '.json',
        base + '/.json',
        'https://api.reddit.com' + parsed.path.rstrip('/') + '.json',
        'https://api.reddit.com' + parsed.path.rstrip('/') + '/.json',
        'https://old.reddit.com' + parsed.path.rstrip('/') + '.json',
        'https://old.reddit.com' + parsed.path.rstrip('/') + '/.json',
    ]
    for t in targets:
        try:
            r = requests.get(t, headers=headers, timeout=15)
            print('TARGET', t)
            print('STATUS', r.status_code)
            print('CT', r.headers.get('content-type'))
            print('HEAD', r.text[:200].replace('\n', ' '))
        except Exception as e:
            print('ERR', t, e)
        print('---')
