import express from 'express';
import { search } from '../service/searchService';
//SEARCH ROUTER
const router = express.Router();

router.get('/search', async (req, res, next) => {
  const title = req.query.title as string;
  const type = req.query.type as 'movie' | 'series';

  if (!title || !type) return res.status(400).json({ error: 'Missing title or type' });

  try {
    const result = await search(title, type);
    res.json(result);
  } catch (err) {
    next(err);  // ⬅ global error handler'a yolla
  }
});

export default router;
