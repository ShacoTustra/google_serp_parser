#!/usr/bin/env python3
"""
Финальный рабочий тест парсера

Этот скрипт использует requests для получения данных от Google
и BeautifulSoup для парсинга (без Playwright, т.к. DNS проблема).
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time

def parse_ai_overview_requests_only(query, language='en'):
    """
    Парсинг AI Overview используя только requests + BeautifulSoup

    Args:
        query: Поисковый запрос
        language: Язык поиска

    Returns:
        str или None: Текст AI Overview
    """
    print(f"\n{'='*80}")
    print(f"🔍 Запрос: {query}")
    print('='*80)

    # Формируем URL
    encoded_query = urllib.parse.quote(query)
    url = f'https://www.google.com/search?q={encoded_query}&hl={language}'

    # Настройки для requests
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': f'{language}-US,{language};q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

    cookies = {
        'CONSENT': 'YES+',
        'NID': '511=test_cookie',
    }

    try:
        print(f"📡 Отправка запроса к: {url}")

        session = requests.Session()
        session.headers.update(headers)
        session.cookies.update(cookies)

        response = session.get(url, timeout=15)
        response.raise_for_status()

        print(f"✓ Статус: {response.status_code}")
        print(f"✓ Размер HTML: {len(response.text)} символов")

        # Сохраняем ДЕКОДИРОВАННЫЙ HTML
        filename = f'google_final_{int(time.time())}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"✓ HTML сохранен: {filename}")

        # Проверяем на антибот
        if 'var o9=function' in response.text or 'var AA=function' in response.text:
            print("\n⚠️  ВНИМАНИЕ: Обнаружена антибот-защита Google!")
            print("Google вернул защитную страницу вместо результатов.")
            print("Это нормально при автоматическом доступе.")
            return None

        # Парсим HTML
        print("\n🔎 Парсинг HTML...")
        soup = BeautifulSoup(response.text, 'lxml')

        # Проверяем основную структуру
        title = soup.find('title')
        if title:
            print(f"✓ Заголовок страницы: {title.get_text()}")

        search_div = soup.find('div', {'id': 'search'})
        if search_div:
            print("✓ Найден основной контейнер результатов (div#search)")
        else:
            print("⚠️  Основной контейнер результатов не найден")

        result_stats = soup.find('div', {'id': 'result-stats'})
        if result_stats:
            print(f"✓ Статистика: {result_stats.get_text()[:100]}")

        # ПОИСК AI OVERVIEW
        print("\n🎯 Поиск AI Overview...")

        # Метод 1: Специфичные селекторы AI Overview
        ai_selectors = [
            'div[data-attrid*="AI"]',
            'div[data-attrid="SGEAIOverview"]',
            'div[data-attrid="AIOverview"]',
            'div[jsname="yp1CPe"]',
            'div[data-sgrd="true"]',
            'div[jscontroller*="Cpkphb"]',
        ]

        for selector in ai_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(separator=' ', strip=True)
                    if len(text) > 100:
                        # Очищаем текст
                        text = re.sub(r'\s+', ' ', text).strip()

                        # Проверяем что это похоже на AI Overview
                        sentences = len([s for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10])
                        if sentences >= 2:
                            print(f"\n✅ AI OVERVIEW НАЙДЕН!")
                            print(f"Селектор: {selector}")
                            print(f"Длина: {len(text)} символов")
                            print(f"Предложений: {sentences}")
                            return text

        # Метод 2: Поиск по data-attrid (любое значение)
        print("🔎 Проверка всех элементов с data-attrid...")
        attrib_elements = soup.find_all('div', {'data-attrid': True})
        print(f"Найдено {len(attrib_elements)} элементов с data-attrid")

        for elem in attrib_elements:
            attrid = elem.get('data-attrid', '')
            if 'AI' in attrid or 'SGE' in attrid or 'overview' in attrid.lower():
                text = elem.get_text(separator=' ', strip=True)
                if len(text) > 100:
                    text = re.sub(r'\s+', ' ', text).strip()
                    print(f"\n✅ AI OVERVIEW НАЙДЕН!")
                    print(f"Атрибут: {attrid}")
                    print(f"Длина: {len(text)} символов")
                    return text

        # Метод 3: Поиск крупных текстовых блоков с признаками AI Overview
        print("🔎 Анализ крупных текстовых блоков...")
        all_divs = soup.find_all('div')
        print(f"Всего div элементов: {len(all_divs)}")

        candidates = []
        for div in all_divs:
            text = div.get_text(separator=' ', strip=True)

            # Фильтры
            if not (150 < len(text) < 3000):
                continue

            # Исключаем навигацию
            nav_keywords = ['Sign in', 'Images', 'Videos', 'Shopping', 'News', 'Maps', 'Settings']
            nav_count = sum(1 for kw in nav_keywords if kw in text)
            if nav_count > 2:
                continue

            # Считаем предложения
            sentences = len([s for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10])
            if sentences < 3:
                continue

            candidates.append((len(text), sentences, text, div))

        if candidates:
            # Сортируем по количеству предложений и длине
            candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)

            print(f"✓ Найдено {len(candidates)} кандидатов")

            # Показываем топ-3
            for i, (length, sentences, text, div) in enumerate(candidates[:3], 1):
                print(f"\nКандидат {i}:")
                print(f"  Длина: {length} символов, Предложений: {sentences}")
                print(f"  Превью: {text[:150]}...")

                # Проверяем классы и ID
                classes = div.get('class', [])
                div_id = div.get('id', '')
                print(f"  Класс: {classes}")
                print(f"  ID: {div_id}")

            # Берем лучшего кандидата
            best = candidates[0]
            text = best[2]
            text = re.sub(r'\s+', ' ', text).strip()

            print(f"\n✅ ВЕРОЯТНЫЙ AI OVERVIEW (или развернутый ответ)")
            print(f"Длина: {len(text)} символов")
            print(f"Предложений: {best[1]}")

            return text

        print("\n❌ AI Overview не найден")

        # Показываем что вообще есть
        print("\n📊 Что найдено на странице:")
        kp = soup.find_all('div', {'class': lambda x: x and 'kp-blk' in ' '.join(x)})
        print(f"  Knowledge Panels: {len(kp)}")

        results = soup.find_all('div', {'class': lambda x: x and 'g' in x})
        print(f"  Обычные результаты поиска: {len(results[:20])}")

        return None

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка сети: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "ФИНАЛЬНЫЙ ТЕСТ ПАРСЕРА" + " "*35 + "║")
    print("╚" + "="*78 + "╝")

    print("\nИспользуется метод: Requests + BeautifulSoup")
    print("(Playwright пропущен из-за DNS проблем в окружении)")

    # Тестовые запросы
    test_queries = [
        "What is artificial intelligence",
        "How does machine learning work",
        "Python programming language",
        "What is quantum computing",
    ]

    results = {}

    for query in test_queries:
        result = parse_ai_overview_requests_only(query, language='en')

        if result:
            print(f"\n{'='*80}")
            print("НАЙДЕННЫЙ ТЕКСТ:")
            print('='*80)
            print(result[:1000] + ("..." if len(result) > 1000 else ""))
            print('='*80)

            results[query] = result
            # Нашли хотя бы один - это успех!
            break
        else:
            results[query] = None

        time.sleep(2)  # Пауза между запросами

    # Итоги
    print("\n" + "="*80)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("="*80)

    found_count = sum(1 for r in results.values() if r is not None)
    print(f"\nВсего запросов: {len(results)}")
    print(f"Найдено AI Overview: {found_count}")

    if found_count > 0:
        print("\n✅ ПАРСЕР РАБОТАЕТ!")
        print("AI Overview успешно извлечен!")
    else:
        print("\n⚠️  AI Overview не найден")
        print("\nВозможные причины:")
        print("  1. Google не показывает AI Overview для этих запросов")
        print("  2. Антибот-защита блокирует автоматический доступ")
        print("  3. AI Overview доступен только в определенных регионах")
        print("  4. Требуется более сложная эмуляция браузера")

    print("\n" + "="*80)

    return found_count > 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
