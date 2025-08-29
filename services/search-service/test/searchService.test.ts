import { search } from '../src/service/searchService';

// Mock the dependencies
jest.mock('../src/dynamodb/search', () => ({
  searchDynamo: jest.fn(),
}));

jest.mock('../src/omdb/search', () => ({
  searchOmdb: jest.fn(),
}));

describe('SearchService', () => {
  it('should return data from OMDB API if available', async () => {
    const mockSearchDynamo = require('../src/dynamodb/search').searchDynamo;
    const mockSearchOmdb = require('../src/omdb/search').searchOmdb;
    
    mockSearchOmdb.mockResolvedValue({ Response: 'True', Title: 'Test Movie from OMDB' });
    
    const result = await search('test', 'movie');
    
    expect(result.source).toBe('omdb');
    expect(result.data.Title).toBe('Test Movie from OMDB');
    expect(mockSearchDynamo).not.toHaveBeenCalled();
  });

  it('should fallback to DynamoDB if OMDB API fails', async () => {
    const mockSearchDynamo = require('../src/dynamodb/search').searchDynamo;
    const mockSearchOmdb = require('../src/omdb/search').searchOmdb;
    
    mockSearchOmdb.mockResolvedValue({ Response: 'False', Error: 'Movie not found!' });
    mockSearchDynamo.mockResolvedValue({ Title: 'Test Movie from DynamoDB' });
    
    const result = await search('test', 'movie');
    
    expect(result.source).toBe('dynamodb');
    expect(result.data.Title).toBe('Test Movie from DynamoDB');
  });

  it('should return not_found if neither source has data', async () => {
    const mockSearchDynamo = require('../src/dynamodb/search').searchDynamo;
    const mockSearchOmdb = require('../src/omdb/search').searchOmdb;
    
    mockSearchOmdb.mockResolvedValue({ Response: 'False', Error: 'Movie not found!' });
    mockSearchDynamo.mockResolvedValue(null);
    
    const result = await search('test', 'movie');
    
    expect(result.source).toBe('not_found');
    expect(result.data.Response).toBe('False');
  });
});
