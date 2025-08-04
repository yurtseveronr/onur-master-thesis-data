// import dotenv from 'dotenv';  ❌ SİL
// dotenv.config();              ❌ SİL

export const config = {
  port: process.env.PORT || 8080,
  omdbApiKey: process.env.OMDB_API_KEY!,
  omdbBaseUrl: process.env.OMDB_BASE_URL!,
  awsRegion: process.env.AWS_REGION!,
  movieTable: process.env.DYNAMODB_MOVIE_TABLE!,
  seriesTable: process.env.DYNAMODB_SERIES_TABLE!,
};
