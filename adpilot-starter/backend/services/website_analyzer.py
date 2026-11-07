"""Membrul 2: extracție simplă; NU accesați URL-uri interne / private în producție."""
import ipaddress
import socket
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

async def extract_website(url: str) -> dict:
    if not url:
        return {'text': '', 'sources': []}
    parsed = urlparse(url)
    if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(400, 'Introdu un URL http(s) valid')
    if parsed.port not in (None, 80, 443):
        raise HTTPException(400, 'Port nepermis')
    try:
        infos = socket.getaddrinfo(parsed.hostname, None)
        if not infos or any(not ipaddress.ip_address(info[4][0]).is_global for info in infos):
            raise ValueError('Adresă internă sau rezervată')
    except (OSError, ValueError):
        raise HTTPException(400, 'Website indisponibil sau adresă nepermisă')
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=False) as client:
            response = await client.get(url, headers={'User-Agent': 'AdPilotHackathon/0.1'})
            response.raise_for_status()
            if 300 <= response.status_code < 400:
                raise ValueError('Redirect nepermis')
            if 'text/html' not in response.headers.get('content-type', ''):
                raise ValueError('Nu este pagină HTML')
            if len(response.content) > 1_000_000:
                raise ValueError('Pagină prea mare')
        soup = BeautifulSoup(response.text, 'html.parser')
        for el in soup(['script', 'style', 'nav', 'footer']): el.decompose()
        text = ' '.join(soup.stripped_strings)[:6000]
        return {'text': text, 'sources': [url]}
    except (httpx.HTTPError, ValueError) as exc:
        return {'text': '', 'sources': [], 'warning': str(exc)}
