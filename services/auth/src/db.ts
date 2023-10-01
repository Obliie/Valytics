import dotenv from 'dotenv';
import mongoose from 'mongoose';
import path from 'path';
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

mongoose.connect(
  `mongodb://${process.env.AUTH_DB_USER}:${process.env.AUTH_DB_PASS}@localhost:${process.env.AUTH_DB_PORT}`,
  {},
);

const db = mongoose.connection;

db.on('error', console.error.bind(console, 'MongoDB connection error:'));
db.once('open', () => {
  console.log('Connected to MongoDB');
});

export default db;
