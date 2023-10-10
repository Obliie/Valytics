import axios from 'axios';
import cookieParser from 'cookie-parser';
import cors from 'cors';
import dotenv from 'dotenv';
import express, { Request, Response } from 'express';
import { sign } from 'jsonwebtoken';
import path from 'path';
import User from './User';
import db from './db';
import auth from './middleware/auth';

dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const app = express();
// MongoDB for auth
const userCollection = db.useDb('auth').collection('users');

app.use(
  cors({
    origin: process.env.CLIENT_REDIRECT_URL,
    credentials: true,
  }),
);

app.use(cookieParser());

// Apply the auth middleware to all routes
app.use(auth);

app.get('/', (_req, res) => {
  res.send('Hello, TypeScript with Express!');
});

app.get('/logout', (req: Request, res: Response) => {
  // Check if there's a logged in user
  if (req.user) {
    // Clear the 'token' cookie to log the user out
    res.clearCookie('token');
    res.redirect(process.env.CLIENT_REDIRECT_URL as string);
  } else {
    res.status(401).send('Not Authenticated');
  }
});

// Route to check if user has been set
app.get('/user', (req: Request, res: Response) => {
  if (req.user) {
    res.send(req.user);
  } else {
    res.status(401).send('Not Authenticated');
  }
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

    // Handle the different endpoints
    if (endpoint === 'LOGIN') {
      console.log('User logged in!');

      // Attempt to find the user
      const fetchedUser = await userCollection.find({ id }).toArray();

      // If the user already exists and isn't logged in set the token
      if (fetchedUser.length > 0 && !req.user) {
        console.log(`Hi ${fetchedUser[0].username}`);
        const token = sign({ sub: id }, process.env.JWT_SECRET as string, { expiresIn: '1d' });
        res.cookie('token', token);
      } else {
        console.log('User not signed up!');
      }
    } else if (endpoint === 'SIGNUP') {
      console.log('User signed up!');

      const user = new User({
        id,
        username,
        email,
      });

      const fetchedUser = await userCollection.find({ id: id }).toArray();

      if (fetchedUser.length > 0) {
        console.log('User already exists!');
      } else {
        console.log('New user!');
        await userCollection.insertOne(user);
      }
    }
    res.redirect(process.env.CLIENT_REDIRECT_URL as string);
  } catch (error) {
    console.error('An error occurred:', error);
    res.redirect(process.env.CLIENT_REDIRECT_URL as string);
  }
};

// Discord login endpoint
app.get('/auth/discord/login', async (_req, res) => {
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
app.get('/auth/discord/signup', async (_req, res) => {
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
