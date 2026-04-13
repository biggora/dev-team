#!/usr/bin/env python3
"""
Web Tester - Site Discovery
Auto-crawls a website to discover pages, forms, links, and interactive elements.

Usage:
    python scripts/discover.py --url https://example.com --output discovery.json
    python scripts/discover.py --url http://localhost:8080 --max-pages 20
"""

import json
import sys
import os
import argparse
from urllib.parse import urljoin, urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed. Install with:")
    print("  pip install playwright && playwright install chromium")
    sys.exit(1)


def discover_site(url, max_pages=10):
    """Crawl site and return structured discovery data."""
    parsed = urlparse(url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"

    visited = set()
    to_visit = [url]
    pages = []

    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        # Register console listener BEFORE any navigation
        # so we catch errors that occur during page load
        console_errors = []
        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)

        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)

            # Clear for each page
            console_errors.clear()

            try:
                page.goto(current_url, wait_until='domcontentloaded', timeout=15000)
                page.wait_for_load_state('networkidle', timeout=8000)
            except Exception as e:
                print(f"  SKIP {current_url}: {e}")
                continue

            page_data = {
                'url': current_url,
                'title': page.title(),
                'headings': [],
                'links': [],
                'forms': [],
                'buttons': [],
                'images': {},
                'nav_items': [],
                'console_errors': list(console_errors)[:5],
            }

            # Headings
            for tag in ['h1', 'h2', 'h3']:
                elements = page.locator(tag).all()
                for el in elements[:5]:
                    try:
                        text = el.text_content().strip()
                        if text:
                            page_data['headings'].append({'tag': tag, 'text': text[:100]})
                    except Exception:
                        pass

            # Navigation
            nav_els = page.locator('nav a, header a, [role=navigation] a').all()
            for el in nav_els[:20]:
                try:
                    text = el.text_content().strip()
                    href = el.get_attribute('href') or ''
                    if text and href:
                        page_data['nav_items'].append({'text': text, 'href': href})
                except Exception:
                    pass

            # All links
            links = page.locator('a[href]').all()
            for link in links[:50]:
                try:
                    href = link.get_attribute('href') or ''
                    text = link.text_content().strip()
                    if href and not href.startswith('#') and not href.startswith('javascript'):
                        full_url = urljoin(current_url, href)
                        page_data['links'].append({'text': text[:60], 'href': full_url})
                        if base_domain in full_url and full_url not in visited:
                            to_visit.append(full_url)
                except Exception:
                    pass

            # Forms
            forms = page.locator('form').all()
            for form in forms:
                try:
                    inputs = form.locator('input, textarea, select').all()
                    buttons = form.locator('button, input[type=submit]').all()
                    form_data = {
                        'action': form.get_attribute('action') or '',
                        'method': form.get_attribute('method') or 'GET',
                        'inputs': [],
                        'submit_buttons': [],
                    }
                    for inp in inputs[:10]:
                        inp_type = inp.get_attribute('type') or 'text'
                        inp_name = inp.get_attribute('name') or inp.get_attribute('id') or ''
                        inp_placeholder = inp.get_attribute('placeholder') or ''
                        form_data['inputs'].append({
                            'type': inp_type,
                            'name': inp_name,
                            'placeholder': inp_placeholder,
                        })
                    for btn in buttons[:3]:
                        btn_text = btn.text_content().strip() or btn.get_attribute('value') or ''
                        form_data['submit_buttons'].append(btn_text)
                    page_data['forms'].append(form_data)
                except Exception:
                    pass

            # Buttons
            buttons = page.locator('button:visible, [role=button]:visible').all()
            for btn in buttons[:15]:
                try:
                    text = btn.text_content().strip()
                    if text:
                        page_data['buttons'].append(text[:60])
                except Exception:
                    pass

            # Images
            images = page.locator('img').all()
            broken = 0
            missing_alt = 0
            for img in images:
                try:
                    natural_w = img.evaluate('el => el.naturalWidth')
                    if natural_w == 0:
                        broken += 1
                    alt = img.get_attribute('alt')
                    if alt is None or alt.strip() == '':
                        missing_alt += 1
                except Exception:
                    pass
            page_data['images'] = {'total': len(images), 'broken': broken, 'missing_alt': missing_alt}

            page_data['console_errors'] = console_errors[:5]
            pages.append(page_data)
            print(f"  ✓ Discovered: {current_url} ({page.title()})")

        browser.close()

    return {
        'base_url': url,
        'pages_found': len(pages),
        'pages': pages,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Tester - Site Discovery')
    parser.add_argument('--url', required=True, help='URL to crawl')
    parser.add_argument('--max-pages', type=int, default=10, help='Max pages to visit')
    parser.add_argument('--output', default='discovery.json', help='Output JSON path')
    args = parser.parse_args()

    print(f"\nDiscovering: {args.url}")
    result = discover_site(args.url, args.max_pages)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nDiscovery complete: {result['pages_found']} pages")
    print(f"Saved to: {args.output}")