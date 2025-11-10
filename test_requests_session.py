#!/usr/bin/env python3
"""
Тест с requests используя сессии и продвинутые anti-detection методы
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse

print("=" * 80)
print("ТЕСТ REQUESTS С СЕССИЯМИ")
print("=" * 80)

def create_session():
    """Создаем сессию с реалистичными headers"""
    session = requests.Session()

    # Устанавливаем реалистичные headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    })

    return session

def fetch_google(session, query):
    """Получаем страницу Google"""
    try:
        # Сначала получаем главную страницу для cookies
        print("🔐 Получаем главную страницу Google для cookies...")
        resp = session.get('https://www.google.com/', timeout=15)
        print(f"   Статус: {resp.status_code}")

        time.sleep(1)

        # Теперь делаем поисковый запрос
        encoded_query = urllib.parse.quote(query)
        search_url = f'https://www.google.com/search?q={encoded_query}&hl=en'

        print(f"🔍 Выполняем поиск...")
        print(f"   URL: {search_url}")

        resp = session.get(search_url, timeout=15)
        print(f"   Статус: {resp.status_code}")
        print(f"   Размер: {len(resp.text)} символов")

        return resp.text

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def check_html_quality(html):
    """Проверяет качество HTML"""
    if not html:
        return False, "No HTML"

    # Проверка на redirect/noscript
    if 'enablejs' in html.lower():
        return False, "JavaScript redirect page"

    if 'javascript is disabled' in html.lower():
        return False, "JavaScript disabled page"

    # Проверка на CAPTCHA
    if 'captcha' in html.lower() or 'recaptcha' in html.lower():
        return False, "CAPTCHA page"

    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all('div')

    if len(divs) < 10:
        return False, f"Too few divs: {len(divs)}"

    # Проверка на наличие результатов поиска
    search_divs = soup.find_all('div', {'data-hveid': True})
    if len(search_divs) == 0:
        return False, "No search result divs"

    return True, f"Valid: {len(divs)} divs, {len(search_divs)} search results"

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
        try:
            elements = soup.select(selector)
            if elements:
                print(f"  Проверяем селектор: {selector} ({len(elements)} найдено)")

            for element in elements:
                text = element.get_text(separator=' ', strip=True)

                if text and len(text) > 100:
                    text = re.sub(r'\s+', ' ', text).strip()
                    sentences = re.split(r'[.!?]+', text)
                    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

                    if len(sentences) >= 2:
                        print(f"✓ Найдено с селектором: {selector}")
                        return text
        except Exception as e:
            print(f"  Ошибка для селектора {selector}: {e}")
            continue

    # Пробуем найти по ключевым словам
    print("\n🔎 Поиск по ключевым словам...")
    all_divs = soup.find_all('div')
    for div in all_divs:
        if div.get('data-attrid'):
            print(f"  data-attrid: {div.get('data-attrid')}")

    return None

# Основной тест
print("\n🚀 Создаем сессию...")
session = create_session()

queries = [
    "What is artificial intelligence",
    "How does machine learning work",
]

for i, query in enumerate(queries, 1):
    print(f"\n{'='*80}")
    print(f"ЗАПРОС {i}/{len(queries)}: {query}")
    print('='*80)

    html = fetch_google(session, query)

    if html:
        # Сохраняем
        filename = f"google_session_{i}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 Сохранено: {filename}")

        # Проверяем качество
        is_valid, msg = check_html_quality(html)
        print(f"\n📊 Качество: {msg}")

        if is_valid:
            print("✅ HTML валиден - есть поисковые результаты!")

            # Ищем AI Overview
            ai_overview = parse_ai_overview(html)

            if ai_overview:
                print(f"\n{'='*80}")
                print("🎉 AI OVERVIEW НАЙДЕН!")
                print('='*80)
                print(ai_overview[:500])
                if len(ai_overview) > 500:
                    print(f"\n... еще {len(ai_overview) - 500} символов")
                print('='*80)

                # Это успех!
                break
            else:
                print("\n⚠️  AI Overview не найден в этом HTML")
                print("Возможные причины:")
                print("  - Google не показывает AI Overview для этого запроса")
                print("  - AI Overview рендерится через JavaScript")
                print("  - Нужны другие селекторы")
        else:
            print(f"❌ HTML невалиден: {msg}")
            print("\nПервые 500 символов:")
            print(html[:500])
    else:
        print("❌ Не удалось получить HTML")

    if i < len(queries):
        print("\n⏸️  Пауза 2 секунды...")
        time.sleep(2)

print("\n" + "=" * 80)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 80)
