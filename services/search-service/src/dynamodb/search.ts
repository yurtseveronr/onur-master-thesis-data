import { ddb } from './client';
import { QueryCommand, ScanCommand } from '@aws-sdk/lib-dynamodb';
import { config } from '../config/env';

// Helper function for case-insensitive search
function normalizeTitle(title: string): string {
  return title.toLowerCase().trim();
}

export async function searchDynamo(title: string, type: string): Promise<any | null> {
  try {
    const TableName = type === 'movie' ? config.movieTable : config.seriesTable;
    const normalizedTitle = normalizeTitle(title);
    console.log(`🗄️ Searching DynamoDB table: ${TableName}`);
    console.log(`🌍 AWS Region: ${config.awsRegion}`);
    console.log(`🔍 Normalized title: "${normalizedTitle}"`);

    // Step 1: Try GSI for exact title match (case-insensitive)
    console.log('🔍 Step 1: Trying GSI for exact title match...');
    try {
      const exactQueryCommand = new QueryCommand({
        TableName,
        IndexName: 'TitleIndex',
        KeyConditionExpression: '#t = :title',
        ExpressionAttributeNames: { '#t': 'Title' },
        ExpressionAttributeValues: { ':title': normalizedTitle },
      });

      const exactResult = await ddb.send(exactQueryCommand);
      
      if (exactResult.Items && exactResult.Items.length > 0) {
        console.log(`✅ Found exact match in GSI: ${exactResult.Items.length} items`);
        return exactResult.Items[0];
      }
    } catch (error) {
      console.log('⚠️ GSI query failed, falling back to scan:', error);
    }

    // Step 2: Try GSI for partial title match
    console.log('🔍 Step 2: Trying GSI for partial title match...');
    try {
      const partialQueryCommand = new QueryCommand({
        TableName,
        IndexName: 'TitleIndex',
        KeyConditionExpression: 'begins_with(#t, :title)',
        ExpressionAttributeNames: { '#t': 'Title' },
        ExpressionAttributeValues: { ':title': normalizedTitle },
        Limit: 5,
      });

      const partialResult = await ddb.send(partialQueryCommand);
      
      if (partialResult.Items && partialResult.Items.length > 0) {
        console.log(`✅ Found partial match in GSI: ${partialResult.Items.length} items`);
        return partialResult.Items[0];
      }
    } catch (error) {
      console.log('⚠️ GSI partial query failed, falling back to scan:', error);
    }

    // Step 3: Fallback to scan for contains matches
    console.log('🔍 Step 3: Trying scan for contains matches...');
    const scanCommand = new ScanCommand({
      TableName,
      FilterExpression: 'contains(lower(#t), :title)',
      ExpressionAttributeNames: { '#t': 'Title' },
      ExpressionAttributeValues: { ':title': normalizedTitle },
      Limit: 10, // Limit results for performance
    });

    console.log(`🔍 DynamoDB scan query: ${normalizedTitle}`);
    const result = await ddb.send(scanCommand);
    
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
