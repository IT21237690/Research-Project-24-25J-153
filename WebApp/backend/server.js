const express = require("express");
const cors = require("cors");
const app = express();
const PORT = 5000;
const fs = require("fs");
const multer = require("multer");
const { spawn } = require("child_process");
app.use(cors());

// Example dataset of sentences
const sentences = {
  beginner: [
    "The cat is on the mat.",
    "She loves ice cream.",
    "I go to school every day.",
  ],
  intermediate: [
    "He is preparing for his exams.",
    "The weather today is quite pleasant.",
    "They are planning a trip to the mountains.",
  ],
  advanced: [
    "Despite the challenges, he managed to complete the project on time.",
    "The intricacies of quantum physics are fascinating.",
    "She eloquently presented her thesis to the committee.",
  ],
};

// Endpoint to fetch a sentence based on the level
app.get("/sentence", (req, res) => {
  const { level } = req.query;

  if (!sentences[level]) {
    return res.status(400).json({ error: "Invalid level selected" });
  }

  // Randomly select a sentence from the level's array
  const sentence =
    sentences[level][Math.floor(Math.random() * sentences[level].length)];
  res.json({ sentence });
});



// Configure Multer for file uploads
const upload = multer({ dest: "uploads/" });

// Analyze endpoint
app.post("/analyze", upload.single("audio"), async (req, res) => {
  const { sentence } = req.body;
  const audioFilePath = req.file.path;

  try {
    // Call Python script for Wav2Vec transcription
    const python = spawn("python3", ["scripts/wav2vec_transcription.py", audioFilePath]);

    let transcription = "";
    python.stdout.on("data", (data) => {
      transcription += data.toString();
    });

    python.stderr.on("data", (data) => {
      console.error(`Error: ${data}`);
    });

    python.on("close", () => {
      // Compare sentences for pronunciation
      const words = sentence.split(" ");
      const transcriptWords = transcription.trim().split(" ");

      const mismatches = words.filter(
        (word, index) => word !== transcriptWords[index]
      );

      const totalTime = transcription.split(" ").length / 2; 
      const fluencyScore = (transcription.split(" ").length / totalTime) * 60;

      res.json({
        transcription: transcription.trim(),
        mismatches,
        fluencyScore: Math.round(fluencyScore),
      });

      // Cleanup
      fs.unlinkSync(audioFilePath);
    });
  } catch (error) {
    console.error("Error processing audio:", error);
    res.status(500).send({ error: "Speech analysis failed" });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
