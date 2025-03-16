const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    firstname: { type: String, required: true },
    lastname: { type: String, required: true },
    username: { type: String, required: true, unique: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role: { type: String, enum: ['student', 'teacher', 'admin'], default: 'student' },
    grade: { type: String, required: true },
    currentDifficulty: { type: Number, required: true, default: 100.0 },
    fluencyDifficulty: { type: Number, required: true, default: 100.0 },
}, { timestamps: true });

module.exports = mongoose.model('User', UserSchema);
