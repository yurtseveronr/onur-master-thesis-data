import axios from 'axios';
import { config } from '../config/env';

//OMDB API CALL
export async function searchOmdb(title: string, type: string): Promise<any> {
  try {
    const params = {
      apikey: config.omdbApiKey,
      t: title,
      type,
      r: 'json',
    };

    const response = await axios.get(config.omdbBaseUrl, { params });
    return response.data;
  } catch (error: any) {
    console.error('OMDB API Error:', error.response?.status, error.response?.data);
    // Return a default response instead of throwing
    return {
      Response: 'False',
      Error: error.response?.data?.Error || 'OMDB API Error'
    };
  }
}
