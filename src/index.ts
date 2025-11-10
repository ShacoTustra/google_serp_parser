import { chromium, Browser, Page } from 'playwright';

/**
 * Configuration options for the AI Overview parser
 */
export interface ParserOptions {
  /**
   * Whether to run browser in headless mode (default: true)
   */
  headless?: boolean;

  /**
   * Timeout for page navigation in milliseconds (default: 30000)
   */
  timeout?: number;

  /**
   * User agent string (optional)
   */
  userAgent?: string;

  /**
   * Language for Google search (default: 'en')
   */
  language?: string;
}

/**
 * Result of AI Overview parsing
 */
export interface AIOverviewResult {
  /**
   * The AI Overview text content
   */
  text: string;

  /**
   * Whether AI Overview was found
   */
  found: boolean;

  /**
   * Search query used
   */
  query: string;

  /**
   * Additional metadata
   */
  metadata?: {
    sources?: string[];
    timestamp?: string;
  };
}

/**
 * Parse AI Overview from Google search results
 *
 * @param query - Search query
 * @param options - Parser configuration options
 * @returns Promise with AI Overview result
 */
export async function parseAIOverview(
  query: string,
  options: ParserOptions = {}
): Promise<AIOverviewResult> {
  const {
    headless = true,
    timeout = 30000,
    userAgent,
    language = 'en'
  } = options;

  let browser: Browser | null = null;
  let page: Page | null = null;

  try {
    // Launch browser
    browser = await chromium.launch({
      headless,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    // Create new page
    const context = await browser.newContext({
      userAgent: userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      locale: language,
      viewport: { width: 1920, height: 1080 }
    });

    page = await context.newPage();
    page.setDefaultTimeout(timeout);

    // Navigate to Google search
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&hl=${language}`;
    await page.goto(searchUrl, { waitUntil: 'networkidle' });

    // Wait a bit for dynamic content to load
    await page.waitForTimeout(2000);

    // Try to find AI Overview block with various selectors
    // Google AI Overview can have different selectors depending on region and updates
    const aiOverviewSelectors = [
      '[data-attrid="SGEAIOverview"]',
      '[data-attrid="AIOverview"]',
      '[jsname="yp1CPe"]', // Common AI Overview container
      '.AI-overview-container',
      '[data-hveid*="CA"]', // Sometimes AI Overview uses specific hveid
      'div[jscontroller][jsname*="yp"]',
      // Additional selectors for AI Overview content
      'div[data-attrid*="AI"]',
      'div[data-attrid*="SGE"]'
    ];

    let aiOverviewText = '';
    let found = false;
    let sources: string[] = [];

    // Try each selector
    for (const selector of aiOverviewSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          // Check if element has meaningful content
          const text = await element.innerText();
          if (text && text.trim().length > 50) { // At least 50 chars to be valid
            aiOverviewText = text.trim();
            found = true;

            // Try to extract sources if available
            try {
              const sourceElements = await element.$$('a[href*="source"], cite, a[data-ved]');
              for (const sourceEl of sourceElements) {
                const href = await sourceEl.getAttribute('href');
                if (href && href.startsWith('http')) {
                  sources.push(href);
                }
              }
            } catch (e) {
              // Sources extraction is optional
            }

            break;
          }
        }
      } catch (e) {
        // Continue to next selector
        continue;
      }
    }

    // If still not found, try a more generic approach looking for AI-generated content indicators
    if (!found) {
      try {
        // Look for text patterns that indicate AI Overview
        const bodyText = await page.content();

        // Check for specific AI Overview markers in the HTML
        if (bodyText.includes('AI Overview') || bodyText.includes('SGE') || bodyText.includes('Generative AI')) {
          // Try to find the main content block
          const possibleContainers = await page.$$('div[data-hveid], div[jscontroller]');

          for (const container of possibleContainers) {
            const text = await container.innerText();
            const html = await container.innerHTML();

            // Check if this looks like an AI Overview block
            if ((html.includes('AI') || html.includes('SGE')) && text.length > 100) {
              aiOverviewText = text.trim();
              found = true;
              break;
            }
          }
        }
      } catch (e) {
        // Generic approach failed
      }
    }

    // Close browser
    await browser.close();

    return {
      text: aiOverviewText,
      found,
      query,
      metadata: {
        sources: sources.length > 0 ? sources : undefined,
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    // Ensure browser is closed on error
    if (browser) {
      await browser.close();
    }

    throw new Error(`Failed to parse AI Overview: ${error instanceof Error ? error.message : String(error)}`);
  }
}

/**
 * Parse AI Overview with existing browser instance
 * Useful for batch processing multiple queries
 *
 * @param browser - Playwright browser instance
 * @param query - Search query
 * @param options - Parser configuration options
 * @returns Promise with AI Overview result
 */
export async function parseAIOverviewWithBrowser(
  browser: Browser,
  query: string,
  options: Omit<ParserOptions, 'headless'> = {}
): Promise<AIOverviewResult> {
  const {
    timeout = 30000,
    userAgent,
    language = 'en'
  } = options;

  const context = await browser.newContext({
    userAgent: userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: language,
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();
  page.setDefaultTimeout(timeout);

  try {
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}&hl=${language}`;
    await page.goto(searchUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Similar parsing logic as above
    const aiOverviewSelectors = [
      '[data-attrid="SGEAIOverview"]',
      '[data-attrid="AIOverview"]',
      '[jsname="yp1CPe"]',
      '.AI-overview-container',
      '[data-hveid*="CA"]',
      'div[jscontroller][jsname*="yp"]',
      'div[data-attrid*="AI"]',
      'div[data-attrid*="SGE"]'
    ];

    let aiOverviewText = '';
    let found = false;
    let sources: string[] = [];

    for (const selector of aiOverviewSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          const text = await element.innerText();
          if (text && text.trim().length > 50) {
            aiOverviewText = text.trim();
            found = true;

            try {
              const sourceElements = await element.$$('a[href*="source"], cite, a[data-ved]');
              for (const sourceEl of sourceElements) {
                const href = await sourceEl.getAttribute('href');
                if (href && href.startsWith('http')) {
                  sources.push(href);
                }
              }
            } catch (e) {
              // Sources extraction is optional
            }

            break;
          }
        }
      } catch (e) {
        continue;
      }
    }

    await context.close();

    return {
      text: aiOverviewText,
      found,
      query,
      metadata: {
        sources: sources.length > 0 ? sources : undefined,
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    await context.close();
    throw new Error(`Failed to parse AI Overview: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export default parseAIOverview;
