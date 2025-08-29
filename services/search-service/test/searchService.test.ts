import { search } from '../src/service/searchService';

// Mock the dependencies
jest.mock('../src/dynamodb/search', () => ({
  searchDynamo: jest.fn(),
}));

jest.mock('../src/omdb/search', () => ({
  searchOmdb: jest.fn(),
}));

describe('SearchService', () => {
  it('should return data from DynamoDB if available', async () => {
    const mockSearchDynamo = require('../src/dynamodb/search').searchDynamo;
    const mockSearchOmdb = require('../src/omdb/search').searchOmdb;
    
    mockSearchDynamo.mockResolvedValue({ Title: 'Test Movie' });
    
    const result = await search('test', 'movie');
    
    expect(result.source).toBe('dynamodb');
    expect(result.data.Title).toBe('Test Movie');
    expect(mockSearchOmdb).not.toHaveBeenCalled();
  });

  it('should fallback to OMDb if DynamoDB returns null', async () => {
    const mockSearchDynamo = require('../src/dynamodb/search').searchDynamo;
    const mockSearchOmdb = require('../src/omdb/search').searchOmdb;
    
    mockSearchDynamo.mockResolvedValue(null);
    mockSearchOmdb.mockResolvedValue({ Title: 'Test Movie from OMDb' });
    
    const result = await search('test', 'movie');
    
    expect(result.source).toBe('omdb');
    expect(result.data.Title).toBe('Test Movie from OMDb');
  });
});
