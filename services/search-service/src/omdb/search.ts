import axios from 'axios';
import { config } from '../config/env';

export async function searchOmdb(title: string, type: string): Promise<any> {
  const params = {
    apikey: config.omdbApiKey,
    t: title,
    type,
    r: 'json',
  };

  const response = await axios.get(config.omdbBaseUrl, { params });
  return response.data;
}
