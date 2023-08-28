const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../../.env') });
import axios from 'axios';
import express from 'express';
const app = express();

app.get('/', (_req, res) => {
  res.send('Hello, TypeScript with Express!');
});

//Discord login endpoint
app.get('/auth/discord/login', async (_req, res) => {
  try {
    const url =
      'https://discord.com/api/oauth2/authorize?client_id=1141746698847260703&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fdiscord%2Fcallback&response_type=code&scope=identify';
    res.redirect(url);
  } catch (error) {
    console.error('An error occurred:', error);
    res.status(500).send('An error occurred');
  }
});

//Callback endpoint after logging in
app.get('/auth/discord/callback', async (req, res) => {
  try {
    const code = req.query.code as string;
    console.log(JSON.stringify(code));
    const params = new URLSearchParams({
      client_id: `${process.env.DISCORD_CLIENT_ID}`,
      client_secret: `${process.env.DISCORD_CLIENT_SECRET}`,
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: `${process.env.DISCORD_REDIRECT_URI}`,
    });

    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept-Encoding': 'application/x-www-form-urlencoded',
    };

    //POST Request to receive access token from Discord
    const response = await axios.post('https://discord.com/api/oauth2/token', params, { headers });
    res.send(response.data);
  } catch (error) {
    console.error('An error occurred:', error);
    res.status(500).send('An error occurred');
  }
});

console.log(process.env.HOST);

const PORT = process.env.NODE_PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
