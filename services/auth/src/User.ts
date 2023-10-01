import mongoose, { Document, Schema } from 'mongoose';

interface IUser extends Document {
  id: string;
  username: string;
  email: string;
}

const userSchema: Schema = new Schema({
  id: { type: String, unique: true },
  username: { type: String },
  email: { type: String },
});

export default mongoose.model<IUser>('User', userSchema);
