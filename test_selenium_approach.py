#!/usr/bin/env python3
"""
Тест с использованием Selenium вместо Playwright
Selenium может иметь другой DNS resolver
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

print("=" * 80)
print("ТЕСТ SELENIUM")
print("=" * 80)

try:
    # Настройки Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    print("\n🚀 Запуск Chrome через Selenium...")
    driver = webdriver.Chrome(options=chrome_options)

    # Тест 1: example.com
    print("\n" + "=" * 80)
    print("ТЕСТ 1: example.com")
    print("=" * 80)

    try:
        driver.get("http://example.com")
        print(f"✅ example.com загружен!")
        print(f"Title: {driver.title}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

    # Тест 2: google.com
    print("\n" + "=" * 80)
    print("ТЕСТ 2: google.com")
    print("=" * 80)

    try:
        url = "https://www.google.com/search?q=What+is+artificial+intelligence"
        print(f"Переход на: {url}")
        driver.get(url)
        time.sleep(3)  # Ждем загрузки

        print(f"✅ Google загружен!")
        print(f"Title: {driver.title}")
        print(f"URL: {driver.current_url}")

        # Сохраняем HTML
        html = driver.page_source
        filename = "google_selenium_test.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 HTML сохранен в: {filename}")
        print(f"Размер HTML: {len(html)} символов")

        # Пробуем найти результаты поиска
        try:
            search_results = driver.find_elements(By.CSS_SELECTOR, "div[data-hveid]")
            print(f"\n📊 Найдено {len(search_results)} блоков с результатами")

            # Пробуем найти AI Overview
            ai_selectors = [
                'div[data-attrid*="AI"]',
                'div[data-attrid*="SGE"]',
                'div[jsname="yp1CPe"]',
                'div[data-sgrd="true"]',
            ]

            print("\n🔎 Поиск AI Overview:")
            for selector in ai_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"  ✓ Найдено {len(elements)} элементов с селектором: {selector}")
                        for i, elem in enumerate(elements[:1]):  # Берем первый
                            text = elem.text
                            if text and len(text) > 50:
                                print(f"\n    Текст элемента {i+1}:")
                                print(f"    {text[:200]}...")
                                print(f"    (Всего {len(text)} символов)")
                except Exception as e:
                    print(f"  ✗ Селектор {selector}: {e}")

        except Exception as e:
            print(f"❌ Ошибка при поиске элементов: {e}")

    except Exception as e:
        print(f"❌ Ошибка при загрузке Google: {e}")
        import traceback
        traceback.print_exc()

    driver.quit()
    print("\n✅ Selenium тест завершен")

except ImportError:
    print("❌ Selenium не установлен!")
    print("Установите: pip install selenium")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
