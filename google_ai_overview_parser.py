#!/usr/bin/env python3
"""
Google AI Overview Parser
Парсер для извлечения AI Overview из результатов поиска Google

Поддерживает два режима:
1. Playwright (для JavaScript-рендеринга, более надежный)
2. Requests (быстрее, но может не работать если AI Overview рендерится через JS)
"""

import re
import time
import urllib.parse
from typing import Optional, Literal
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class GoogleAIOverviewParser:
    """Парсер для извлечения AI Overview из Google"""

    def __init__(
        self,
        method: Literal['playwright', 'requests'] = 'playwright',
        headless: bool = True,
        save_html: bool = False
    ):
        """
        Инициализация парсера

        Args:
            method: Метод парсинга ('playwright' или 'requests')
            headless: Запуск браузера в headless режиме (только для playwright)
            save_html: Сохранять HTML страницы для отладки
        """
        self.method = method
        self.headless = headless
        self.save_html = save_html

    def parse(self, query: str, language: str = 'en') -> Optional[str]:
        """
        Парсинг AI Overview для заданного запроса

        Args:
            query: Поисковый запрос
            language: Язык поиска (en, ru, и т.д.)

        Returns:
            Текст AI Overview или None если не найден
        """
        print(f"\n🔍 Поиск AI Overview для запроса: '{query}'")
        print(f"Язык: {language}")
        print(f"Метод: {self.method}")

        if self.method == 'playwright':
            return self._parse_with_playwright(query, language)
        elif self.method == 'requests':
            return self._parse_with_requests(query, language)
        else:
            raise ValueError(f"Неизвестный метод: {self.method}")

    def _parse_with_playwright(self, query: str, language: str) -> Optional[str]:
        """Парсинг с использованием Playwright"""
        with sync_playwright() as p:
            # Запускаем браузер
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            # Создаем контекст с настройками
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale=language
            )

            page = context.new_page()

            try:
                # Формируем URL для поиска
                encoded_query = urllib.parse.quote(query)
                search_url = f'https://www.google.com/search?q={encoded_query}&hl={language}'

                print(f"📡 Переход на: {search_url}")

                # Переходим на страницу
                page.goto(search_url, wait_until='networkidle', timeout=30000)

                # Ждем загрузки контента
                time.sleep(3)

                # Сохраняем HTML если нужно
                if self.save_html:
                    html = page.content()
                    filename = f"google_page_{int(time.time())}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"💾 HTML сохранен в: {filename}")

                # Ищем AI Overview по различным селекторам
                ai_overview_text = self._extract_ai_overview_from_page(page)

                if ai_overview_text:
                    print(f"✅ AI Overview найден! Длина: {len(ai_overview_text)} символов")
                else:
                    print("❌ AI Overview не найден")

                return ai_overview_text

            except PlaywrightTimeoutError:
                print("⏱️ Timeout при загрузке страницы")
                return None
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                return None
            finally:
                context.close()
                browser.close()

    def _parse_with_requests(self, query: str, language: str) -> Optional[str]:
        """Парсинг с использованием requests + BeautifulSoup"""
        try:
            import requests
            from bs4 import BeautifulSoup

            # Формируем URL
            encoded_query = urllib.parse.quote(query)
            search_url = f'https://www.google.com/search?q={encoded_query}&hl={language}'

            print(f"📡 Запрос к: {search_url}")

            # Выполняем запрос
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': f'{language},en;q=0.9',
            }

            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            # Сохраняем HTML если нужно
            if self.save_html:
                filename = f"google_page_{int(time.time())}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 HTML сохранен в: {filename}")

            # Парсим HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Ищем AI Overview
            ai_overview_text = self._extract_ai_overview_from_soup(soup)

            if ai_overview_text:
                print(f"✅ AI Overview найден! Длина: {len(ai_overview_text)} символов")
            else:
                print("❌ AI Overview не найден")

            return ai_overview_text

        except ImportError:
            print("❌ Ошибка: Установите requests и beautifulsoup4")
            print("   pip install requests beautifulsoup4 lxml")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка сети: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

    def _extract_ai_overview_from_page(self, page) -> Optional[str]:
        """
        Извлечение текста AI Overview из Playwright page

        Args:
            page: Playwright page объект

        Returns:
            Текст AI Overview или None
        """
        # Список селекторов для поиска AI Overview
        selectors = [
            # Основные селекторы Google AI Overview
            'div[data-attrid*="AI"]',
            'div[data-attrid*="SGE"]',
            'div[jsname="yp1CPe"]',
            'div[jscontroller*="Cpkphb"]',
            'div.AI-overview-container',
            'div[data-hveid*="CAEQ"] div[data-attrid]',
            # Более общие селекторы
            'div[data-sgrd="true"]',
            'div.kp-blk.knowledge-panel',
            'div.xpdopen',
            # Новые селекторы 2024
            'div[data-attrid="SGEAIOverview"]',
            'div[data-attrid="AIOverview"]',
        ]

        print("🔎 Поиск AI Overview с различными селекторами...")

        for selector in selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text()

                    # Проверяем, что это похоже на AI Overview
                    if text and len(text) > 100:
                        # Очищаем текст от лишних символов
                        text = self._clean_text(text)

                        # Дополнительная проверка на признаки AI Overview
                        if self._is_likely_ai_overview(text):
                            print(f"✓ Найдено с селектором: {selector}")
                            return text

            except Exception as e:
                continue

        # Если стандартные селекторы не сработали, пробуем поиск по тексту
        print("🔎 Пробуем альтернативный метод поиска...")
        return self._find_by_content_analysis(page)

    def _extract_ai_overview_from_soup(self, soup) -> Optional[str]:
        """
        Извлечение текста AI Overview из BeautifulSoup объекта

        Args:
            soup: BeautifulSoup объект

        Returns:
            Текст AI Overview или None
        """
        # CSS селекторы для поиска
        selectors = [
            'div[data-attrid*="AI"]',
            'div[data-attrid*="SGE"]',
            'div[jsname="yp1CPe"]',
            'div[data-sgrd="true"]',
            'div[data-attrid="SGEAIOverview"]',
            'div[data-attrid="AIOverview"]',
        ]

        print("🔎 Поиск AI Overview в HTML...")

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(separator=' ', strip=True)

                if text and len(text) > 100:
                    text = self._clean_text(text)

                    if self._is_likely_ai_overview(text):
                        print(f"✓ Найдено с селектором: {selector}")
                        return text

        return None

    def _find_by_content_analysis(self, page) -> Optional[str]:
        """Поиск AI Overview путем анализа содержимого всех div-блоков"""
        try:
            # Получаем все крупные div-блоки
            divs = page.query_selector_all('div[data-hveid], div[jscontroller]')
            print(f"Анализирую {len(divs)} блоков...")

            for div in divs[:30]:  # Проверяем первые 30 блоков
                try:
                    text = div.inner_text()

                    if text and len(text) > 150 and len(text) < 5000:
                        # Проверяем признаки AI Overview
                        if self._is_likely_ai_overview(text):
                            text = self._clean_text(text)
                            print(f"✓ Найдено через анализ контента")
                            return text

                except:
                    continue

        except Exception as e:
            print(f"Ошибка при анализе контента: {e}")

        return None

    def _is_likely_ai_overview(self, text: str) -> bool:
        """
        Проверка, что текст похож на AI Overview

        Args:
            text: Текст для проверки

        Returns:
            True если похож на AI Overview
        """
        if len(text) < 100 or len(text) > 5000:
            return False

        # Подсчитываем количество предложений
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # AI Overview обычно содержит несколько предложений
        if len(sentences) < 2:
            return False

        # Проверяем, что это не навигационные элементы
        nav_keywords = ['Sign in', 'Settings', 'Privacy', 'Terms', 'About', 'Images', 'Videos', 'News', 'Shopping', 'Maps']
        nav_count = sum(1 for keyword in nav_keywords if keyword.lower() in text.lower())

        if nav_count > 3:
            return False

        return True

    def _clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов"""
        # Убираем множественные пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Убираем лишние пробелы в начале и конце
        text = text.strip()
        return text


def parse_ai_overview(
    query: str,
    method: Literal['playwright', 'requests'] = 'playwright',
    headless: bool = True,
    save_html: bool = False,
    language: str = 'en'
) -> Optional[str]:
    """
    Удобная функция для парсинга AI Overview

    Args:
        query: Поисковый запрос
        method: Метод парсинга ('playwright' или 'requests')
        headless: Запуск браузера в headless режиме
        save_html: Сохранять HTML для отладки
        language: Язык поиска

    Returns:
        Текст AI Overview или None
    """
    parser = GoogleAIOverviewParser(
        method=method,
        headless=headless,
        save_html=save_html
    )
    return parser.parse(query, language=language)


if __name__ == '__main__':
    # Тестирование парсера
    print("=" * 80)
    print("Google AI Overview Parser - Тест")
    print("=" * 80)

    # Тестовые запросы (на английском AI Overview встречается чаще)
    test_queries = [
        "What is artificial intelligence",
        "How does photosynthesis work",
    ]

    print("\n🔷 Тест с Playwright:")
    print("-" * 80)

    for query in test_queries:
        result = parse_ai_overview(
            query,
            method='playwright',
            headless=True,
            save_html=False,
            language='en'
        )

        if result:
            print(f"\n{'='*80}")
            print(f"Запрос: {query}")
            print(f"{'='*80}")
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"{'='*80}\n")
        else:
            print(f"\n❌ Для запроса '{query}' AI Overview не найден\n")

        time.sleep(2)  # Пауза между запросами

    print("\n" + "=" * 80)
    print("Тест завершен!")
    print("=" * 80)
