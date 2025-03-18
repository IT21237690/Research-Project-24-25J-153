const mongoose = require('mongoose');

const QASchema = new mongoose.Schema({
    user_id: { type: String, required: true },
    ReferenceText: String,
    PronunciationScore: Number,
    SpeakingRate: Number,
    MispronouncedWords: Array,

});

module.exports = mongoose.model('fluency_results', QASchema);
