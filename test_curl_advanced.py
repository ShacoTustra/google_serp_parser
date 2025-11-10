#!/usr/bin/env python3
"""
Продвинутый подход с curl - пробуем обойти защиту Google
"""

import subprocess
import urllib.parse
from bs4 import BeautifulSoup
import re
import time

print("=" * 80)
print("ПРОДВИНУТЫЙ ТЕСТ С CURL")
print("=" * 80)

def fetch_google_with_curl_advanced(query):
    """
    Получить страницу Google с продвинутыми настройками curl
    """
    encoded_query = urllib.parse.quote(query)
    url = f'https://www.google.com/search?q={encoded_query}&hl=en'

    # Создаем временный файл для cookies
    cookie_file = '/tmp/google_cookies.txt'

    try:
        # Шаг 1: Получаем основную страницу Google с cookies
        print(f"\n📡 URL: {url}")
        print("🔐 Используем продвинутые headers и cookies...")

        result = subprocess.run(
            [
                'curl',
                '-s',  # Silent
                '-L',  # Follow redirects
                '-c', cookie_file,  # Save cookies
                '-b', cookie_file,  # Load cookies
                '--compressed',  # Handle compression
                '-H', 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                '-H', 'Accept-Language: en-US,en;q=0.9',
                '-H', 'Accept-Encoding: gzip, deflate, br',
                '-H', 'Connection: keep-alive',
                '-H', 'Upgrade-Insecure-Requests: 1',
                '-H', 'Sec-Fetch-Dest: document',
                '-H', 'Sec-Fetch-Mode: navigate',
                '-H', 'Sec-Fetch-Site: none',
                '-H', 'Sec-Fetch-User: ?1',
                '-H', 'Cache-Control: max-age=0',
                url
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"❌ curl error code: {result.returncode}")
            print(f"stderr: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def check_html_quality(html):
    """Проверяет качество полученного HTML"""
    if not html:
        return False, "No HTML"

    # Проверка на redirect/noscript страницу
    if 'enablejs' in html.lower() or 'javascript is disabled' in html.lower():
        return False, "JavaScript redirect page"

    # Проверка наличия поисковых результатов
    if 'search' not in html.lower():
        return False, "No search content"

    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all('div')

    if len(divs) < 10:
        return False, f"Too few divs: {len(divs)}"

    return True, f"Valid HTML with {len(divs)} divs"

def parse_ai_overview(html):
    """Парсинг AI Overview"""
    soup = BeautifulSoup(html, 'lxml')

    selectors = [
        'div[data-attrid*="AI"]',
        'div[data-attrid*="SGE"]',
        'div[jsname="yp1CPe"]',
        'div[data-sgrd="true"]',
        'div[data-attrid="SGEAIOverview"]',
        'div[data-attrid="AIOverview"]',
    ]

    print("\n🔎 Поиск AI Overview...")

    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            text = element.get_text(separator=' ', strip=True)

            if text and len(text) > 100:
                text = re.sub(r'\s+', ' ', text).strip()
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

                if len(sentences) >= 2:
                    print(f"✓ Найдено с селектором: {selector}")
                    return text

    return None

# Тест
queries = [
    "What is artificial intelligence",
    "How does machine learning work",
]

for i, query in enumerate(queries, 1):
    print(f"\n{'='*80}")
    print(f"ЗАПРОС {i}: {query}")
    print('='*80)

    html = fetch_google_with_curl_advanced(query)

    if html:
        print(f"✅ Получен HTML: {len(html)} символов")

        # Сохраняем
        filename = f"google_curl_adv_{query.replace(' ', '_')[:20]}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 Сохранено: {filename}")

        # Проверяем качество
        is_valid, msg = check_html_quality(html)
        print(f"📊 Качество HTML: {msg}")

        if is_valid:
            print("✅ HTML валиден!")

            # Ищем AI Overview
            ai_overview = parse_ai_overview(html)

            if ai_overview:
                print(f"\n🎉 AI OVERVIEW НАЙДЕН!")
                print("=" * 80)
                print(ai_overview[:500])
                if len(ai_overview) > 500:
                    print(f"\n... еще {len(ai_overview) - 500} символов")
                print("=" * 80)
            else:
                print("\n⚠️  AI Overview не найден")
        else:
            print(f"❌ HTML невалиден: {msg}")
            print("\nПервые 500 символов:")
            print(html[:500])
    else:
        print("❌ Не удалось получить HTML")

    if i < len(queries):
        print("\n⏸️  Пауза 3 секунды...")
        time.sleep(3)

print("\n" + "=" * 80)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 80)
