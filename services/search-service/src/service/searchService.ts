import { searchDynamo } from '../dynamodb/search';
import { searchOmdb } from '../omdb/search';

export async function search(title: string, type: 'movie' | 'series'): Promise<any> {
  console.log(`🔍 Searching for: "${title}" (${type})`);
  
  const normalizedTitle = title.toLowerCase();
  
  // Step 1: Try OMDB API first
  console.log('📡 Step 1: Trying OMDB API...');
  try {
    const omdbResult = await searchOmdb(title, type);
    console.log('✅ OMDB API Response:', omdbResult);
    
    if (omdbResult && omdbResult.Response === 'True') {
      console.log('🎯 Found in OMDB API!');
      return { 
        source: 'omdb', 
        data: omdbResult,
        message: 'Found in OMDB API'
      };
    } else {
      console.log('❌ Not found in OMDB API:', omdbResult?.Error || 'Unknown error');
    }
  } catch (error) {
    console.error('🔥 OMDB API Error:', error);
  }
  
  // Step 2: Try DynamoDB database
  console.log('🗄️ Step 2: Trying DynamoDB database...');
  try {
    const dynamoResult = await searchDynamo(normalizedTitle, type);
    if (dynamoResult) {
      console.log('✅ Found in DynamoDB!');
      return { 
        source: 'dynamodb', 
        data: dynamoResult,
        message: 'Found in DynamoDB'
      };
    } else {
      console.log('❌ Not found in DynamoDB');
    }
  } catch (error) {
    console.error('🔥 DynamoDB Error:', error);
  }
  
  // Step 3: Return not found
  console.log('❌ Not found anywhere');
  return { 
    source: 'not_found', 
    data: { 
      Response: 'False', 
      Error: 'Movie/Series not found in any source' 
    },
    message: 'Not found in OMDB API or DynamoDB'
  };
}
