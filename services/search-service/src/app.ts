import express from 'express';
import searchRouter from './api/searchRouter';
import { config } from './config/env';
//express app
const app = express();
app.use(express.json());
app.use('/api', searchRouter);

app.use((err: any, _req: any, res: any, _next: any) => {
  console.error('🔥 Global Error:', err.stack || err.message || err);
  res.status(500).json({ error: 'Internal Error' });
});

app.listen(config.port, () => {
  console.log(`🚀 Search service running on port ${config.port}`);
});
