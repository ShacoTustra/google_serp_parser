#!/usr/bin/env python3
"""Анализ HTML от Google для поиска AI Overview"""

from bs4 import BeautifulSoup
import re
import sys

def analyze_html_file(filename):
    """Анализировать HTML файл"""
    print(f"\n{'='*80}")
    print(f"Анализ файла: {filename}")
    print('='*80)

    with open(filename, 'r', encoding='utf-8') as f:
        html = f.read()

    print(f"Размер HTML: {len(html)} символов")

    soup = BeautifulSoup(html, 'lxml')

    # Проверка 1: Антибот защита
    print("\n📋 Проверка 1: Антибот-защита")
    if 'var o9=function' in html or 'var AA=function' in html:
        print("⚠️  ОБНАРУЖЕНА антибот-защита Google!")
        print("Google вернул защитную страницу вместо результатов поиска")
        return False
    else:
        print("✓ Антибот-защиты не обнаружено")

    # Проверка 2: Основная структура
    print("\n📋 Проверка 2: Основная структура страницы")

    title = soup.find('title')
    if title:
        print(f"✓ Заголовок: {title.get_text()}")

    search_div = soup.find('div', {'id': 'search'})
    if search_div:
        print("✓ Найден div#search (контейнер результатов)")
    else:
        print("✗ div#search не найден")

    result_stats = soup.find('div', {'id': 'result-stats'})
    if result_stats:
        print(f"✓ Статистика: {result_stats.get_text()}")
    else:
        print("✗ Статистика не найдена")

    # Проверка 3: Поиск AI Overview селекторов
    print("\n📋 Проверка 3: Поиск AI Overview")

    ai_selectors = [
        ('div[data-attrid*="AI"]', 'data-attrid содержит AI'),
        ('div[data-attrid="SGEAIOverview"]', 'SGEAIOverview'),
        ('div[data-attrid="AIOverview"]', 'AIOverview'),
        ('div[jsname="yp1CPe"]', 'jsname yp1CPe'),
        ('div[data-sgrd="true"]', 'data-sgrd true'),
    ]

    for selector, description in ai_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"\n✓ Найдено {len(elements)} элементов с {description}")
            for i, elem in enumerate(elements[:2], 1):
                text = elem.get_text(separator=' ', strip=True)
                print(f"  Элемент {i}: {len(text)} символов")
                if len(text) > 100:
                    print(f"  Превью: {text[:200]}...")
                    return text  # Нашли!
        else:
            print(f"✗ {description}: не найдено")

    # Проверка 4: Поиск по data-attrid (все варианты)
    print("\n📋 Проверка 4: Все элементы с data-attrid")

    attrib_elements = soup.find_all('div', {'data-attrid': True})
    print(f"Найдено {len(attrib_elements)} элементов с data-attrid")

    if attrib_elements:
        print("\nПервые 10 значений data-attrib:")
        for i, elem in enumerate(attrib_elements[:10], 1):
            attrid = elem.get('data-attrid')
            text_len = len(elem.get_text(strip=True))
            print(f"  {i}. {attrid} (текст: {text_len} символов)")

    # Проверка 5: Анализ всех крупных текстовых блоков
    print("\n📋 Проверка 5: Крупные текстовые блоки")

    all_divs = soup.find_all('div')
    print(f"Всего div элементов: {len(all_divs)}")

    large_blocks = []
    for div in all_divs:
        text = div.get_text(separator=' ', strip=True)
        if 150 < len(text) < 3000:
            # Проверяем что это не навигация
            nav_count = sum(1 for kw in ['Sign in', 'Images', 'Videos', 'Shopping', 'News'] if kw in text)
            if nav_count < 2:
                large_blocks.append((len(text), text, div))

    print(f"Найдено {len(large_blocks)} крупных блоков (150-3000 символов, не навигация)")

    if large_blocks:
        # Сортируем по размеру
        large_blocks.sort(reverse=True)

        print("\nТоп-5 самых крупных блоков:")
        for i, (length, text, div) in enumerate(large_blocks[:5], 1):
            print(f"\n  {i}. Длина: {length} символов")
            print(f"     Класс: {div.get('class', 'нет')}")
            print(f"     ID: {div.get('id', 'нет')}")
            print(f"     Превью: {text[:150]}...")

            # Проверяем признаки AI Overview
            sentences = len([s for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10])
            print(f"     Предложений: {sentences}")

            if sentences >= 3:
                print(f"     ✓ Похоже на связный текст (AI Overview candidate)")
                print(f"\n{'='*80}")
                print("ПОТЕНЦИАЛЬНЫЙ AI OVERVIEW НАЙДЕН:")
                print('='*80)
                print(text[:800])
                print('='*80)
                return text

    print("\n❌ AI Overview не найден ни одним методом")

    # Проверка 6: Что вообще есть на странице
    print("\n📋 Проверка 6: Общая информация о странице")

    # Ищем knowledge panel
    kp = soup.find('div', {'class': 'kp-blk'})
    if kp:
        print("✓ Найден Knowledge Panel")

    # Ищем обычные результаты поиска
    search_results = soup.find_all('div', {'class': 'g'})
    print(f"✓ Найдено обычных результатов поиска: {len(search_results)}")

    # Ищем featured snippets
    featured = soup.find_all('div', {'data-attrid': re.compile('wa:/description|kc:/local')})
    print(f"✓ Найдено featured snippets: {len(featured)}")

    return None


if __name__ == '__main__':
    import glob

    html_files = glob.glob('google_hybrid_*.html') + glob.glob('google_improved_*.html')

    if not html_files:
        print("❌ HTML файлы не найдены")
        sys.exit(1)

    print(f"\nНайдено {len(html_files)} HTML файлов")

    for filename in html_files[:3]:  # Анализируем первые 3
        result = analyze_html_file(filename)
        if result:
            print(f"\n🎉 УСПЕХ! AI Overview найден в {filename}")
            print(f"\nПолный текст ({len(result)} символов):")
            print("="*80)
            print(result)
            print("="*80)
            break

    print("\n" + "="*80)
    print("Анализ завершен")
    print("="*80)
