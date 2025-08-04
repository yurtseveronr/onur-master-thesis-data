import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { config } from '../config/env';

const client = new DynamoDBClient({ region: config.awsRegion });
export const ddb = DynamoDBDocumentClient.from(client);
