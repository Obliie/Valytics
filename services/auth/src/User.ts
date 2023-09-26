import mongoose, { Document, Schema } from 'mongoose';

interface IUser extends Document {
  discordId: string;
  username: string;
}

const userSchema: Schema = new Schema({
  discordId: { type: String, required: true, unique: true },
  username: { type: String, required: true },
});

export default mongoose.model<IUser>('User', userSchema);
