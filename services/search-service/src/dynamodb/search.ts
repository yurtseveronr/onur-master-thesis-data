import { ddb } from './client';
import { ScanCommand } from '@aws-sdk/lib-dynamodb';
import { config } from '../config/env';

export async function searchDynamo(title: string, type: string): Promise<any | null> {
  try {
    const TableName = type === 'movie' ? config.movieTable : config.seriesTable;
    console.log(`🗄️ Searching DynamoDB table: ${TableName}`);

    const command = new ScanCommand({
      TableName,
      FilterExpression: 'contains(#t, :title)',
      ExpressionAttributeNames: { '#t': 'Title' },
      ExpressionAttributeValues: { ':title': title },
    });

    console.log(`🔍 DynamoDB search query: ${title}`);
    const result = await ddb.send(command);
    
    if (result.Items && result.Items.length > 0) {
      console.log(`✅ Found ${result.Items.length} items in DynamoDB`);
      return result.Items[0];
    } else {
      console.log('❌ No items found in DynamoDB');
      return null;
    }
  } catch (error) {
    console.error('🔥 DynamoDB search error:', error);
    return null;
  }
}
