import axios from 'axios';
import dotenv from 'dotenv';
import express from 'express';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const app = express();

app.get('/', (_req, res) => {
  res.send('Hello, TypeScript with Express!');
});

// Function to handle Discord callback after logging in/signing up
const handleDiscordOAuth = async (
  req: express.Request,
  res: express.Response,
  endpoint: string,
  redirectUri: string,
) => {
  try {
    console.log(`${endpoint} ENDPOINT`);
    console.log(req.query);

    if (req.query.error) {
      // User canceled authorization
      console.log('User canceled authorization');
      // You can display a message or take other actions here
      return res.status(400).send('Authorization cancelled by the user');
    }

    // If there is no error parameter, continue with the OAuth flow
    const code = req.query.code as string;
    const params = new URLSearchParams({
      client_id: process.env.DISCORD_CLIENT_ID!,
      client_secret: process.env.DISCORD_CLIENT_SECRET!,
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
    });

    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept-Encoding': 'application/x-www-form-urlencoded',
    };

    // POST Request to receive access token from Discord
    const response = await axios.post('https://discord.com/api/oauth2/token', params, { headers });
    const userResponse = await axios.get('https://discord.com/api/users/@me', {
      headers: {
        Authorization: `Bearer ${response.data.access_token}`,
        ...headers,
      },
    });

    // Get user details
    const { id, username, email } = userResponse.data;

    // TODO: Handle additional logic based on the endpoint
    if (endpoint === 'LOGIN') {
      console.log('User logged in!');
    } else if (endpoint === 'SIGNUP') {
      console.log('User signed up!');
    }

    res.send(userResponse.data);
  } catch (error) {
    console.error('An error occurred:', error);
    res.status(500).send('An error occurred');
  }
};

// Discord login endpoint
app.get('/auth/discord/login', async (req, res) => {
  try {
    const url =
      'https://discord.com/api/oauth2/authorize?client_id=1141746698847260703&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fdiscord%2Flogin%2Fcallback&response_type=code&scope=identify';
    res.redirect(url);
  } catch (error) {
    console.error('An error occurred:', error);
    res.status(500).send('An error occurred');
  }
});

// Discord sign up endpoint
app.get('/auth/discord/signup', async (req, res) => {
  try {
    const url =
      'https://discord.com/api/oauth2/authorize?client_id=1141746698847260703&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fdiscord%2Fsignup%2Fcallback&response_type=code&scope=identify';
    res.redirect(url);
  } catch (error) {
    console.error('An error occurred:', error);
    res.status(500).send('An error occurred');
  }
});

// Discord login callback endpoint
app.get('/auth/discord/login/callback', async (req, res) => {
  await handleDiscordOAuth(req, res, 'LOGIN', process.env.DISCORD_LOGIN_REDIRECT_URI!);
});

// Discord signup callback endpoint
app.get('/auth/discord/signup/callback', async (req, res) => {
  await handleDiscordOAuth(req, res, 'SIGNUP', process.env.DISCORD_SIGNUP_REDIRECT_URI!);
});

console.log(process.env.HOST);

const PORT = process.env.NODE_PORT ?? 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
