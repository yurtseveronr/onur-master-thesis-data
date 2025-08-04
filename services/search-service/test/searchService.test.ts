import { search } from '../src/service/searchService';
import { searchDynamo } from '../src/dynamodb/search';
import { searchOmdb } from '../src/omdb/search';

jest.mock('../src/dynamodb/search');
jest.mock('../src/omdb/search');

describe('searchService', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('returns data from DynamoDB if available', async () => {
    (searchDynamo as jest.Mock).mockResolvedValue({ Title: 'From DynamoDB' });
    const result = await search('inception', 'movie');

    expect(searchDynamo).toHaveBeenCalledWith('inception', 'movie');
    expect(result.source).toBe('dynamodb');
    expect(result.data.Title).toBe('From DynamoDB');
    expect(searchOmdb).not.toHaveBeenCalled();
  });

  it('falls back to OMDb if DynamoDB returns null', async () => {
    (searchDynamo as jest.Mock).mockResolvedValue(null);
    (searchOmdb as jest.Mock).mockResolvedValue({ Title: 'From OMDb' });

    const result = await search('inception', 'movie');

    expect(searchDynamo).toHaveBeenCalled();
    expect(searchOmdb).toHaveBeenCalledWith('inception', 'movie');
    expect(result.source).toBe('omdb');
    expect(result.data.Title).toBe('From OMDb');
  });
});
