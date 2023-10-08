import { NextFunction, Request, Response } from 'express';
import { verify } from 'jsonwebtoken';
import db from '../db';

const auth = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // Check if the 'token' cookie is present in the request
    const token = req.cookies.token;

    if (!token) {
      // If the token is not present, set req.user to null
      req.user = null;
      return next();
    } else {
      // Verify the token
      const { sub } = await verify(token, process.env.JWT_SECRET as string);

      // Fetch user data from the database based on the token
      const findUser = await db.useDb('auth').collection('users').find({ id: sub }).toArray();

      // Store user data in req.user
      req.user = findUser[0];

      // Continue processing the request
      next();
    }
  } catch (error) {
    // Handle errors, such as token validation errors
    console.log('Errors in auth: ', error);
    req.user = null;
    next();
  }
};

export default auth;
