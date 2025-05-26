import React, { useState } from 'react';
import axios from 'axios';
import styled from 'styled-components';

// Container for the entire app
const AppContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  background-color: #1b263b;
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 20px;
  position: relative;
  overflow: hidden;

  /* First background image */
  &::before {
    content: '';
    position: absolute;
    top: 80%;  /* Different position */
    left: 92%;
    transform: translate(-50%, -50%) rotate(-30deg); /* Negative rotation */
    width: 500px;
    height: 500px;
    background-image: url(${process.env.PUBLIC_URL}/images/monster.png); /* Different image */
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.5;
    z-index: 0;
  }

  /* Second background image */
  &::after {
    content: '';
    position: absolute;
    top: 76%;
    left: 9%;
    transform: translate(-50%, -50%) rotate(20deg);
    width: 600px;
    height: 600px;
    background-image: url(${process.env.PUBLIC_URL}/images/monster2.png);
    background-size: contain;
    background-repeat: no-repeat;
    opacity: 0.5;
    z-index: 0;
  }
`;

// Left Column Styling
const LeftColumn = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* Align the content to the top */
  align-items: center;
  background-color: #0d1b2a;  /* Dark blue */
  border-radius: 10px;
  padding: 20px;
  margin-right: 20px;
  width: 40%;
  position: relative;
`;

// Right Column Styling
const RightColumn = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: flex-start; /* Align content to the top */
  background-color: #0d1b2a;
  border-radius: 10px;
  padding: 20px;
  width: 40%;
  height: 80%;
  overflow-y: auto; /* Allow scrolling if content overflows */
`;

// Buttons
const Button = styled.button`
  background-color: #345bde;
  color: white;
  font-size: 14px;  /* Smaller font size */
  border: none;
  padding: 8px 20px;  /* Adjust padding */
  margin: 10px;
  cursor: pointer;
  border-radius: 5px;
  transition: all 0.3s ease;
  align-self: center;

  &:hover {
    background-color: #1e1e1e;
  }

  &:disabled {
    background-color: #778da9;
    cursor: not-allowed;
  }
`;

// Input for text description
const InputField = styled.textarea`
  padding: 10px;
  font-size: 16px;
  width: 80%;
  max-width: 500px; /* Control the max width */
  height: 150px; /* Make the box taller */
  margin: 10px auto; /* Center horizontally */
  border-radius: 5px;
  border: 1px solid #ccc;
  background-color: #345bde;
  color: white;
  resize: none;  /* Remove resize handle */

  &:focus {
    outline: none;
    border-color: #1e1e1e;
  }
`;

// Feedback Box for Grammar and Similarity
const FeedbackBox = styled.div`
  background-color: #1e1e1e;
  color: white;
  padding: 15px;
  width: 100%;  /* Ensure it fits in the right column */
  margin-top: 20px;
  border-radius: 5px;
  font-size: 14px;
  height: 150px;
  overflow-y: auto; /* Allow scrolling if content overflows */
  white-space: pre-line; /* This ensures that line breaks are displayed correctly */
`;

// Heading Styling for "See and Describe"
const Heading = styled.h1`
  font-size: 24px;
  color: #e0e1dd;  /* Light color for the title */
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
`;

// Style for "Suggested fix" in grammar feedback
const SuggestedFix = styled.span`
  font-weight: bold;
  color: #34b7f1; /* Highlight color */
`;

const SimilarityScore = styled.span`
  font-weight: bold;
  color: #34b7f1; /* Highlighted color for the percentage */
  font-size: 18px;
`;

const FinalScoreText = styled.div`
  font-weight: bold;
  color: #34b7f1; /* Highlight color for the score */
  font-size: 18px;
`;

const FinalFeedbackText = styled.div`
  font-weight: bold;
  color: #34b7f1; /* Highlight color for the feedback */
  font-size: 18px;
`;

const ResetMessage = styled.div`
  font-weight: bold;
  color: #34b7f1;
  font-size: 18px;
  margin-top: 20px;
`;

const ImageDesc = () => {
  const [image, setImage] = useState(null);
  const [text, setText] = useState('');
  const [similarityScores, setSimilarityScores] = useState([]);  // Track similarity scores for each attempt
  const [similarityFeedback, setSimilarityFeedback] = useState('');
  const [grammarFeedback, setGrammarFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [finalScore, setFinalScore] = useState(null);
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const [isStarted, setIsStarted] = useState(false);
  const [resetMessage, setResetMessage] = useState('');  // Added state to store reset message

  const generateImage = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/generate-image');
      console.log("Generated Image Base64:", response.data.image);  // Log base64 for debugging
      setImage(response.data.image);  // base64 image string
      setSelectedPrompt(response.data.prompt);  // Store the selected prompt

      // Clear the description and feedback when generating a new image
      setText('');  // Clear the description text
      setGrammarFeedback('');  // Clear grammar feedback
      setSimilarityFeedback('');  // Clear similarity feedback
      setSimilarityScores([]);  // Clear similarity scores
      setFinalScore(null);  // Reset final score

      setLoading(false);
    } catch (error) {
      console.error("Error generating image:", error);
      setLoading(false);
    }
  };

  const checkGrammar = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/check-grammar', { text });
      setGrammarFeedback(response.data.feedback);
      setLoading(false);
    } catch (error) {
      console.error("Error checking grammar:", error);
      setLoading(false);
    }
  };

  const checkSimilarity = async () => {
    setLoading(true);
    try {
      if (!selectedPrompt) {
        alert("Please generate an image first!");
        return;
      }

      const response = await axios.post('http://localhost:5000/check-similarity', { text, prompt: selectedPrompt });
      const similarityScore = response.data.similarity_score;
      setSimilarityScores([...similarityScores, similarityScore]);  // Accumulate similarity scores
      setSimilarityFeedback(response.data.feedback);
      setLoading(false);
    } catch (error) {
      console.error("Error checking similarity:", error);
      setLoading(false);
    }
  };

  const fetchFinalScore = () => {
    // Send similarity scores to the backend for final calculation
    if (similarityScores.length > 0) {
      axios.post('http://localhost:5000/final-score', { similarity_scores: similarityScores })
        .then((response) => {
          const finalScore = response.data.final_score;
          const feedback = response.data.feedback;
          
          // Set the final score and feedback on the frontend
          setFinalScore({ averageScore: finalScore, feedback: feedback });
        })
        .catch((error) => {
          console.error("Error fetching final score:", error);
        });
    }
  };

  const resetSession = () => {
    setSimilarityScores([]);  // Clear the similarity scores
    setSimilarityFeedback('');
    setGrammarFeedback('');
    setText('');  // Clear the description text
    setImage(null);
    setSelectedPrompt('');
    setFinalScore(null);
    setIsStarted(false);
    setResetMessage('New session started! All previous results cleared.');

    // Fetch final score after session reset
    fetchFinalScore();
  };

  const startQuiz = () => {
    setIsStarted(true);
    generateImage();
  };

  // Process feedback to add line breaks and number the errors
  const processFeedback = (feedback) => {
    let counter = 1;
    return feedback.split("\n").map((line, index) => {
      // Add line spacing after "Suggestions for you to keep in mind:"
      if (line === "Suggestions for you to keep in mind:") {
        return (
          <div key={index}>
            <span>{line}</span>
            <br />
            <br /> {/* Add extra line break here */}
          </div>
        );
      }

      // If line contains 'Suggested fix:', wrap it in the SuggestedFix component
      if (line.includes("Suggested fix:")) {
        return (
          <div key={index}>
            <span>{counter++}. </span>
            {line.split("Suggested fix:")[0]}
            <SuggestedFix>
              {" Suggested fix:" + line.split("Suggested fix:")[1]}
            </SuggestedFix>
            <br /> {/* Add line break after each suggestion */}
          </div>
        );
      }

      // Otherwise just render the line
      return <div key={index}>{line}<br/></div>;
    });
  };

  return (
    <AppContainer>
      <LeftColumn>
        {/* Heading Added Here */}
        <Heading>See and Describe</Heading>

        <Button onClick={startQuiz} disabled={loading}>
          {loading ? 'Starting...' : 'Lets Start! 🥳'}
        </Button>
        {isStarted && (
          <Button onClick={generateImage} disabled={loading}>
            {loading ? 'Generating Image...' : 'Lets Go To The Next Image! 🤗'}
          </Button>
        )}
        <Button onClick={resetSession} disabled={loading}>
          {loading ? 'Resetting...' : 'New Session Please! 😴'}
        </Button>

        {/* Displaying the generated image */}
        {image ? (
          <div>
            <img src={`data:image/png;base64,${image}`} alt="Generated" style={{ width: '100%', height: 'auto' }} />
          </div>
        ) : (
          <div style={{ color: 'white' }}>Image will appear here</div>
        )}

        {/* Display reset message */}
        {resetMessage && (
          <FeedbackBox>
            <p>{resetMessage}</p>
          </FeedbackBox>
        )}

        {/* Display final feedback */}
        {finalScore && (
          <FeedbackBox>
            <h3>Final Score</h3>
            <FinalScoreText>
              Average Similarity Score: {finalScore.averageScore.toFixed(2)}%
            </FinalScoreText>
            <FinalFeedbackText>{finalScore.feedback}</FinalFeedbackText>
          </FeedbackBox>
        )}
      </LeftColumn>

      <RightColumn>
        {/* Center-aligning the heading */}
        <Heading>Let's describe the Image!</Heading>
        
        <InputField
          placeholder="Enter your description here"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <Button onClick={checkGrammar} disabled={loading}>
          {loading ? 'Checking Grammar...' : 'Check My Grammar! 🫣'}
        </Button>
        <Button onClick={checkSimilarity} disabled={loading}>
          {loading ? 'Checking Similarity...' : 'Did I Describe Correctly? 🧐'}
        </Button>

        <FeedbackBox>
          {similarityScores.length > 0 && (
            <>
              <h3>Similarity Score: <SimilarityScore>{(similarityScores[similarityScores.length - 1] * 100).toFixed(2)}%</SimilarityScore></h3>
              <p>{similarityFeedback}</p>
              <p><strong>Expected Description: </strong>{selectedPrompt}</p>
              <p><strong>Your Description: </strong>{text}</p> {/* Added user's description */}
            </>
          )}
        </FeedbackBox>

        <FeedbackBox>
          {grammarFeedback && (
            <>
              <h3>Grammar Feedback:</h3>
              <p>
                {processFeedback(grammarFeedback)}
              </p>
            </>
          )}
        </FeedbackBox>
      </RightColumn>
    </AppContainer>
  );
};

export default ImageDesc;
