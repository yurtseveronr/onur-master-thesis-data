import { ddb } from './client';
import { ScanCommand } from '@aws-sdk/lib-dynamodb';
import { config } from '../config/env';

export async function searchDynamo(title: string, type: string): Promise<any | null> {
  const TableName = type === 'movie' ? config.movieTable : config.seriesTable;

  const command = new ScanCommand({
    TableName,
    FilterExpression: 'contains(#t, :title)',
    ExpressionAttributeNames: { '#t': 'Title' },
    ExpressionAttributeValues: { ':title': title },
  });

  const result = await ddb.send(command);
  return result.Items?.length ? result.Items[0] : null;
}
