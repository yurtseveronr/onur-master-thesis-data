import { ddb } from './client';
import { ScanCommand } from '@aws-sdk/lib-dynamodb';
import { config } from '../config/env';

export async function searchDynamo(title: string, type: string): Promise<any | null> {
  try {
    const TableName = type === 'movie' ? config.movieTable : config.seriesTable;
    console.log(`🗄️ Searching DynamoDB table: ${TableName}`);
    console.log(`🌍 AWS Region: ${config.awsRegion}`);

    // First, try to list tables to see if we can connect
    console.log('🔌 Testing DynamoDB connection...');
    
    // Simple contains search - DynamoDB doesn't support case-insensitive search natively
    const command = new ScanCommand({
      TableName,
      FilterExpression: 'contains(#t, :title)',
      ExpressionAttributeNames: { '#t': 'Title' },
      ExpressionAttributeValues: { ':title': title },
    });

    console.log(`🔍 DynamoDB search query: ${title}`);
    const result = await ddb.send(command);
    
    console.log(`📊 DynamoDB scan result: ${result.Items?.length || 0} items found`);
    
    if (result.Items && result.Items.length > 0) {
      console.log(`✅ Found ${result.Items.length} items in DynamoDB`);
      console.log('📋 First item:', result.Items[0]);
      return result.Items[0];
    } else {
      console.log('❌ No items found in DynamoDB');
      return null;
    }
  } catch (error: any) {
    console.error('🔥 DynamoDB search error:', error);
    console.error('🔥 Error details:', error.message);
    return null;
  }
}
