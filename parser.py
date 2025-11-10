"""
Google AI Overview Parser
Парсер для извлечения AI Overview блока из результатов поиска Google
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, Page, Playwright
import time


@dataclass
class AIOverviewResult:
    """Результат парсинга AI Overview"""
    text: str
    found: bool
    query: str
    sources: Optional[List[str]] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            'text': self.text,
            'found': self.found,
            'query': self.query,
            'sources': self.sources,
            'timestamp': self.timestamp
        }


class GoogleAIOverviewParser:
    """Парсер для Google AI Overview"""

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
        language: str = 'en'
    ):
        """
        Инициализация парсера

        Args:
            headless: Запускать браузер в headless режиме
            timeout: Таймаут для операций (мс)
            user_agent: Пользовательский User Agent
            language: Язык поиска
        """
        self.headless = headless
        self.timeout = timeout
        self.user_agent = user_agent or (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
        self.language = language

    def parse(self, query: str) -> AIOverviewResult:
        """
        Парсинг AI Overview для заданного запроса

        Args:
            query: Поисковый запрос

        Returns:
            AIOverviewResult с результатами парсинга
        """
        with sync_playwright() as playwright:
            return self._parse_with_playwright(playwright, query)

    def _parse_with_playwright(
        self,
        playwright: Playwright,
        query: str
    ) -> AIOverviewResult:
        """Внутренний метод парсинга с Playwright"""

        # Попытка использовать уже установленный браузер
        browser_path = '/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome'
        import os
        if os.path.exists(browser_path):
            browser = playwright.chromium.launch(
                headless=self.headless,
                executable_path=browser_path,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
        else:
            browser = playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

        try:
            context = browser.new_context(
                user_agent=self.user_agent,
                locale=self.language,
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.new_page()
            page.set_default_timeout(self.timeout)

            # Переходим на страницу поиска Google
            search_url = f'https://www.google.com/search?q={query}&hl={self.language}'
            print(f"Navigating to: {search_url}")

            try:
                page.goto(search_url, wait_until='domcontentloaded', timeout=self.timeout)
                # Ждем загрузки динамического контента
                time.sleep(3)
            except Exception as e:
                print(f"Navigation error: {e}")
                print("Note: This may be due to network restrictions in the environment")
                raise

            # Пробуем найти AI Overview с разными селекторами
            ai_overview_text = ''
            found = False
            sources = []

            # Список селекторов для поиска AI Overview
            selectors = [
                'div[data-attrid="SGEAIOverview"]',
                'div[data-attrid="AIOverview"]',
                'div[jsname="yp1CPe"]',
                'div.AI-overview-container',
                'div[data-hveid*="CA"]',
                'div[jscontroller][jsname*="yp"]',
                'div[data-attrid*="AI"]',
                'div[data-attrid*="SGE"]',
                # Дополнительные селекторы
                'div[data-ai-overview]',
                'div.sgE',
                'div#rso div[jscontroller]:has-text("AI")',
            ]

            print("Searching for AI Overview with multiple selectors...")

            for selector in selectors:
                try:
                    print(f"Trying selector: {selector}")
                    element = page.query_selector(selector)

                    if element:
                        text = element.inner_text()
                        print(f"Found element with text length: {len(text) if text else 0}")

                        if text and len(text.strip()) > 50:
                            ai_overview_text = text.strip()
                            found = True
                            print(f"✓ Found AI Overview with selector: {selector}")

                            # Пытаемся извлечь источники
                            try:
                                source_elements = element.query_selector_all('a[href^="http"]')
                                for source_el in source_elements:
                                    href = source_el.get_attribute('href')
                                    if href and href.startswith('http'):
                                        sources.append(href)
                            except Exception as e:
                                print(f"Could not extract sources: {e}")

                            break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue

            # Если не нашли стандартными селекторами, пробуем более общий подход
            if not found:
                print("Standard selectors failed, trying generic approach...")
                try:
                    # Ищем блоки с текстом, который может быть AI Overview
                    all_divs = page.query_selector_all('div[data-hveid], div[jscontroller]')
                    print(f"Found {len(all_divs)} potential containers")

                    for div in all_divs[:20]:  # Проверяем первые 20 блоков
                        try:
                            text = div.inner_text()
                            html = div.inner_html()

                            # Проверяем признаки AI Overview
                            if (
                                text and len(text) > 100 and
                                ('AI' in html or 'overview' in html.lower() or 'SGE' in html)
                            ):
                                ai_overview_text = text.strip()
                                found = True
                                print(f"✓ Found AI Overview using generic approach")
                                break
                        except:
                            continue

                except Exception as e:
                    print(f"Generic approach failed: {e}")

            # Если все еще не нашли, попробуем скриншот для отладки
            if not found and not self.headless:
                print("AI Overview not found. Check the browser window.")
                time.sleep(5)

            context.close()
            browser.close()

            return AIOverviewResult(
                text=ai_overview_text,
                found=found,
                query=query,
                sources=sources if sources else None,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            browser.close()
            raise Exception(f"Failed to parse AI Overview: {str(e)}")


def parse_ai_overview(
    query: str,
    headless: bool = True,
    timeout: int = 30000,
    user_agent: Optional[str] = None,
    language: str = 'en'
) -> AIOverviewResult:
    """
    Удобная функция для парсинга AI Overview

    Args:
        query: Поисковый запрос
        headless: Запускать браузер в headless режиме
        timeout: Таймаут для операций (мс)
        user_agent: Пользовательский User Agent
        language: Язык поиска

    Returns:
        AIOverviewResult с результатами парсинга
    """
    parser = GoogleAIOverviewParser(
        headless=headless,
        timeout=timeout,
        user_agent=user_agent,
        language=language
    )
    return parser.parse(query)


if __name__ == '__main__':
    # Тестовый запуск
    print("Testing Google AI Overview Parser\n")

    query = "What is artificial intelligence?"
    print(f"Query: {query}\n")

    result = parse_ai_overview(query, headless=True)

    if result.found:
        print("✅ AI Overview found!")
        print(f"\nText ({len(result.text)} chars):")
        print("-" * 80)
        print(result.text[:500] + ('...' if len(result.text) > 500 else ''))
        print("-" * 80)

        if result.sources:
            print(f"\nSources: {len(result.sources)}")
            for i, source in enumerate(result.sources[:5], 1):
                print(f"  {i}. {source}")
    else:
        print("❌ AI Overview not found")
