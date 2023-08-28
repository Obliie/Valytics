const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../../.env') });
import express from 'express';
const app = express();

app.get('/', (_req, res) => {
  res.send('Hello, TypeScript with Express!');
});

app.get('/auth/discord/login', (_req, res) => {
  const url =
    'https://discord.com/api/oauth2/authorize?client_id=1141746698847260703&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fdiscord%2Fcallback&response_type=code&scope=identify';
  res.redirect(url);
});

console.log(process.env.HOST);

const PORT = process.env.NODE_PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
