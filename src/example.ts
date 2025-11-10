import { parseAIOverview, ParserOptions } from './index';

/**
 * Example usage of Google AI Overview parser
 */
async function main() {
  console.log('Google AI Overview Parser Example\n');
  console.log('=================================\n');

  // Example 1: Basic usage
  console.log('Example 1: Basic search query');
  console.log('Query: "What is artificial intelligence?"\n');

  try {
    const result1 = await parseAIOverview('What is artificial intelligence?', {
      headless: true,
      timeout: 30000
    });

    if (result1.found) {
      console.log('✅ AI Overview found!');
      console.log('\nAI Overview Text:');
      console.log('-'.repeat(80));
      console.log(result1.text);
      console.log('-'.repeat(80));

      if (result1.metadata?.sources && result1.metadata.sources.length > 0) {
        console.log('\nSources:');
        result1.metadata.sources.forEach((source, index) => {
          console.log(`  ${index + 1}. ${source}`);
        });
      }
    } else {
      console.log('❌ AI Overview not found for this query');
      console.log('Note: AI Overview may not be available for all queries or regions');
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
  }

  console.log('\n' + '='.repeat(80) + '\n');

  // Example 2: Another query
  console.log('Example 2: Technical query');
  console.log('Query: "How does machine learning work?"\n');

  try {
    const result2 = await parseAIOverview('How does machine learning work?', {
      headless: true,
      language: 'en'
    });

    if (result2.found) {
      console.log('✅ AI Overview found!');
      console.log('\nAI Overview Text:');
      console.log('-'.repeat(80));
      console.log(result2.text.substring(0, 500) + (result2.text.length > 500 ? '...' : ''));
      console.log('-'.repeat(80));
      console.log(`\nFull text length: ${result2.text.length} characters`);
    } else {
      console.log('❌ AI Overview not found for this query');
    }
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
  }

  console.log('\n' + '='.repeat(80));
  console.log('Examples completed!');
}

// Run the example
main().catch(console.error);
