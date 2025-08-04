import { searchDynamo } from '../dynamodb/search';
import { searchOmdb } from '../omdb/search';

export async function search(title: string, type: 'movie' | 'series'): Promise<any> {
  const normalizedTitle = title.toLowerCase();
  const dynamoResult = await searchDynamo(normalizedTitle, type);
  if (dynamoResult) return { source: 'dynamodb', data: dynamoResult };

  const omdbResult = await searchOmdb(normalizedTitle, type);
  return { source: 'omdb', data: omdbResult };
}
