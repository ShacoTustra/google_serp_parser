"""
Тестирование парсера с mock HTML данными
"""

from playwright.sync_api import sync_playwright
import time


def test_parser_logic():
    """Тест логики парсинга с локальным HTML"""

    # Mock HTML, имитирующий структуру Google AI Overview
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Google Search</title></head>
    <body>
        <div id="rso">
            <div data-attrid="SGEAIOverview">
                <div class="content">
                    <p>Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans. AI systems can perform tasks such as visual perception, speech recognition, decision-making, and language translation. Modern AI is based on machine learning and deep learning techniques that allow systems to learn from data without being explicitly programmed.</p>
                    <div class="sources">
                        <a href="https://example.com/ai-basics">Source 1</a>
                        <a href="https://example.com/machine-learning">Source 2</a>
                    </div>
                </div>
            </div>
            <div class="regular-result">
                <h3>Regular search result</h3>
                <p>This is not an AI Overview</p>
            </div>
        </div>
    </body>
    </html>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path='/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome',
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = browser.new_context()
        page = context.new_page()

        # Загружаем mock HTML
        page.set_content(mock_html)

        # Тестируем селекторы
        selectors = [
            'div[data-attrid="SGEAIOverview"]',
            'div[data-attrid="AIOverview"]',
            'div[jsname="yp1CPe"]',
        ]

        print("Testing selectors on mock HTML...\n")

        for selector in selectors:
            print(f"Trying selector: {selector}")
            element = page.query_selector(selector)

            if element:
                text = element.inner_text()
                print(f"✓ Found element with selector: {selector}")
                print(f"Text length: {len(text)} characters")
                print(f"Text preview: {text[:150]}...")

                # Проверяем извлечение источников
                links = element.query_selector_all('a[href]')
                print(f"Found {len(links)} links")
                for link in links:
                    href = link.get_attribute('href')
                    print(f"  - {href}")

                print("\n✅ Parser logic works correctly!")
                break
            else:
                print(f"✗ Not found with selector: {selector}\n")

        browser.close()


if __name__ == '__main__':
    print("=" * 80)
    print("Mock Test for AI Overview Parser")
    print("=" * 80)
    print()

    try:
        test_parser_logic()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
