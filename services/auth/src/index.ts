import 'dotenv/config';
import express from 'express';

const app = express();

app.get('/', (_req, res) => {
  res.send('Hello, TypeScript with Express!');
});

const PORT = process.env.NODE_PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`ENV PORT: ${process.env.NODE_PORT}`);
});
