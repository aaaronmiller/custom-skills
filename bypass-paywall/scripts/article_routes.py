#!/usr/bin/env python3
"""Build alternate article URLs offline. No network requests or page claims."""
import argparse
import ipaddress
import json
from urllib.parse import quote, urlencode, urlsplit, urlunsplit


def routes(url):
    if any(ord(c) < 32 for c in url):
        raise ValueError('URL contains control characters')
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Use an absolute public HTTP(S) URL without credentials')
    host = p.hostname.lower().rstrip('.')
    if host == 'localhost' or host.endswith(('.localhost', '.local')) or '.' not in host:
        raise ValueError('Local targets are not article-service inputs')
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError('Nonpublic IP targets are not article-service inputs')
    _ = p.port  # Reject malformed ports before generating routes.
    clean = urlunsplit((p.scheme, p.netloc, p.path, p.query, ''))
    return {
        'original': clean,
        'archive_today_lookup': 'https://archive.today/newest/' + quote(clean, safe=''),
        'wayback_availability': 'https://archive.org/wayback/available?' + urlencode({'url': clean}),
        'jina_reader': 'https://r.jina.ai/' + clean,
        'status': 'candidates_only',
        'notice': 'Offline URL construction only. Check URL privacy before requesting; verify each response.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    args = parser.parse_args()
    try:
        result = routes(args.url)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
