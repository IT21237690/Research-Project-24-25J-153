const mongoose = require('mongoose');

const QASchema = new mongoose.Schema({
    user_id: { type: String, required: true },
    passage: String,
    question: String,
    user_answer: String,
    gold_answer: String,
    similarity: Number,
    readability: Number,
    updated_difficulty: Number
});

module.exports = mongoose.model('qa_results', QASchema);
