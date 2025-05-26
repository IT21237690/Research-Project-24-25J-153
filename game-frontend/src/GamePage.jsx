import React, { useState, useEffect } from "react";
import {
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Typography,
  Button,
  CircularProgress,
  Chip,
  Container,
  Box,
  Grid,
  Paper,
  LinearProgress,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from "@mui/material";
import { styled } from "@mui/material/styles";
import LightbulbIcon from "@mui/icons-material/Lightbulb";
import FavoriteIcon from "@mui/icons-material/Favorite";
import EmojiEventsIcon from "@mui/icons-material/EmojiEvents";
import api from "./api";



const StyledCard = styled(Card)(({ theme }) => ({
  borderRadius: 16,
  boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
  overflow: "hidden",
  position: "relative",
  transition: "transform 0.3s ease",
  "&:hover": {
    transform: "translateY(-5px)",
  },
}));

const StyledChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  fontWeight: 600,
  boxShadow: "0 2px 5px rgba(0,0,0,0.08)",
}));

const ObjectRecognitionGame = () => {
  const [gameState, setGameState] = useState({
    level: 1,
    score: 0,
    highScore: 0,
    chances: 3,
    maxChances: 3,
    consecutiveFailures: 0,
    consecutiveSuccesses: 0,
    currentImage: "",
    objectsToFind: [],
    answerOptions: [],
    selectedAnswers: [],
    gameStatus: "loading",
    isAuthenticated: false,
    userId: null,
    username: "Guest",
    hint: false,
    timeRemaining: 30,
    difficulty: 1,
  });

  const [alert, setAlert] = useState({
    open: false,
    message: "",
    severity: "info",
  });

  const [dialogOpen, setDialogOpen] = useState(false);
  const [timer, setTimer] = useState(null);

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const response = await api.get("/auth/me");
        if (response.data.success) {
          setGameState((prev) => ({
            ...prev,
            isAuthenticated: true,
            userId: response.data.user._id,
            username: response.data.user.username,
            highScore: response.data.user.highScore || 0,
            level: response.data.user.currentLevel || 1,
            difficulty: response.data.user.difficulty || 1,
          }));
        }
      } catch (error) {
        console.log("Not authenticated, playing as guest");
      } finally {
        loadNewImage();
      }
    };

    checkAuth();

    // Cleanup function
    return () => {
      if (timer) clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (gameState.gameStatus === "playing" && gameState.timeRemaining > 0) {
      const countdown = setInterval(() => {
        setGameState((prev) => {
          const newTime = prev.timeRemaining - 1;
          if (newTime <= 0) {
            clearInterval(countdown);
            return {
              ...prev,
              timeRemaining: 0,
              gameStatus: "timeout",
              consecutiveFailures: prev.consecutiveFailures + 1,
              consecutiveSuccesses: 0,
            };
          }
          return { ...prev, timeRemaining: newTime };
        });
      }, 1000);

      setTimer(countdown);

      return () => clearInterval(countdown);
    }
  }, [gameState.gameStatus, gameState.timeRemaining]);

  const loadNewImage = async () => {
    setGameState((prev) => ({
      ...prev,
      gameStatus: "loading",
      selectedAnswers: [],
      timeRemaining: 60 - prev.difficulty * 2, // Adjust time based on difficulty
    }));

    try {
      const response = await api.get(
        `/game/new-round?difficulty=${gameState.difficulty}`
      );

      if (response.data.success) {
        const { imageUrl, objectsToFind, answerOptions } = response.data;

        setGameState((prev) => ({
          ...prev,
          currentImage: imageUrl,
          objectsToFind: objectsToFind,
          answerOptions: answerOptions,
          chances: prev.maxChances,
          gameStatus: "playing",
          hint: false,
        }));

        // Start timer for this round
        if (timer) clearInterval(timer);
      } else {
        throw new Error("Failed to load image");
      }
    } catch (error) {
      console.error("Error loading new image:", error);
      setAlert({
        open: true,
        message: "Failed to load new image. Please try again.",
        severity: "error",
      });

      // Fallback to mock data if API fails
      const mockImageData = {
        imageUrl: "/img.png",
        objectsToFind: ["cat", "ball", "book"],
        answerOptions: ["cat", "ball", "book", "dog", "car", "tree"].sort(
          () => Math.random() - 0.5
        ),
      };

      setGameState((prev) => ({
        ...prev,
        currentImage: mockImageData.imageUrl,
        objectsToFind: mockImageData.objectsToFind,
        answerOptions: mockImageData.answerOptions,
        chances: prev.maxChances,
        gameStatus: "playing",
        hint: false,
      }));
    }
  };

  const handleAnswerSelect = (answer) => {
    if (
      gameState.gameStatus !== "playing" ||
      gameState.selectedAnswers.includes(answer)
    ) {
      return;
    }

    const newSelectedAnswers = [...gameState.selectedAnswers, answer];
    const isCorrect = gameState.objectsToFind.includes(answer);

    if (!isCorrect) {
      const newChances = gameState.chances - 1;
      const gameStatus = newChances <= 0 ? "failed" : "playing";

      setGameState((prev) => ({
        ...prev,
        chances: newChances,
        selectedAnswers: newSelectedAnswers,
        gameStatus,
        consecutiveFailures:
          gameStatus === "failed"
            ? prev.consecutiveFailures + 1
            : prev.consecutiveFailures,
        consecutiveSuccesses: 0,
      }));

      setAlert({
        open: true,
        message: "Oops! That's not in the image.",
        severity: "error",
      });
    } else {
      // Check if all objects are found
      const correctFound = newSelectedAnswers.filter((item) =>
        gameState.objectsToFind.includes(item)
      ).length;

      const allObjectsFound = correctFound === gameState.objectsToFind.length;
      const gameStatus = allObjectsFound ? "success" : "playing";
      const newScore = (prev) => prev.score + 10 * gameState.difficulty;

      setGameState((prev) => ({
        ...prev,
        selectedAnswers: newSelectedAnswers,
        score: newScore(prev),
        highScore: Math.max(newScore(prev), prev.highScore),
        gameStatus,
        consecutiveSuccesses:
          gameStatus === "success"
            ? prev.consecutiveSuccesses + 1
            : prev.consecutiveSuccesses,
        consecutiveFailures: 0,
      }));

      if (allObjectsFound) {
        if (timer) clearInterval(timer);

        setAlert({
          open: true,
          message: "Great job! You found all objects!",
          severity: "success",
        });

        // Save score if authenticated
        if (gameState.isAuthenticated) {
          api
            .post("/game/save-score", {
              userId: gameState.userId,
              score: newScore(gameState),
              level: gameState.level,
              difficulty: gameState.difficulty,
            })
            .catch((err) => console.error("Error saving score:", err));
        }
      } else {
        setAlert({
          open: true,
          message: "Correct! Keep going!",
          severity: "success",
        });
      }
    }
  };

  const showHint = () => {
    const foundObjects = gameState.selectedAnswers.filter((item) =>
      gameState.objectsToFind.includes(item)
    );

    const remainingObjects = gameState.objectsToFind.filter(
      (item) => !foundObjects.includes(item)
    );

    if (remainingObjects.length > 0) {
      setGameState((prev) => ({
        ...prev,
        hint: true,
      }));

      setAlert({
        open: true,
        message: `Look for: ${remainingObjects[0]}`,
        severity: "info",
      });
    }
  };

  const nextRound = async () => {
    let newLevel = gameState.level;
    let newDifficulty = gameState.difficulty;

    // Adjust difficulty based on performance
    if (gameState.consecutiveFailures >= 5) {
      newDifficulty = Math.max(1, gameState.difficulty - 1);
      setDialogOpen(true);
    } else if (gameState.consecutiveSuccesses >= 3) {
      newDifficulty = Math.min(5, gameState.difficulty + 1);
      newLevel = Math.min(10, gameState.level + 1);
      setDialogOpen(true);
    }

    setGameState((prev) => ({
      ...prev,
      level: newLevel,
      difficulty: newDifficulty,
      gameStatus: "loading",
    }));

    // Update user progress if authenticated
    if (gameState.isAuthenticated) {
      await api
        .post("/game/update-progress", {
          userId: gameState.userId,
          level: newLevel,
          difficulty: newDifficulty,
        })
        .catch((err) => console.error("Error updating progress:", err));
    }

    loadNewImage();
  };

  const handleCloseAlert = () => {
    setAlert({
      ...alert,
      open: false,
    });
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <StyledCard>
        <CardHeader
          title={
            <Typography variant="h4" fontWeight="bold" align="center">
              Image Explorer - Level {gameState.level}
            </Typography>
          }
          subheader={
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              mt={1}
            >
              <StyledChip
                icon={<EmojiEventsIcon />}
                label={`Score: ${gameState.score}`}
                color="primary"
                variant="outlined"
              />
              <StyledChip
                icon={<FavoriteIcon />}
                label={`Lives: ${gameState.chances}`}
                color="error"
                variant="outlined"
              />
              <StyledChip
                label={`Difficulty: ${gameState.difficulty}`}
                color="secondary"
                variant="outlined"
              />
            </Box>
          }
        />

        <LinearProgress
          variant="determinate"
          value={(gameState.timeRemaining / 30) * 100}
          color={gameState.timeRemaining < 10 ? "error" : "primary"}
          sx={{ height: 8, mx: 2 }}
        />

        <CardContent>
          {gameState.gameStatus === "loading" ? (
            <Box
              display="flex"
              flexDirection="column"
              alignItems="center"
              my={8}
            >
              <CircularProgress size={60} />
              <Typography variant="h6" mt={2}>
                Loading new challenge...
              </Typography>
            </Box>
          ) : (
            <>
              <Box display="flex" justifyContent="center" mb={3}>
                <Paper
                  elevation={8}
                  sx={{
                    position: "relative",
                    overflow: "hidden",
                    borderRadius: 4,
                    width: "60%",
                  }}
                >
                  <img
                    src={gameState.currentImage}
                    alt="Find the objects"
                    style={{
                      width: "100%",
                      display: "block",
                      borderRadius: 16,
                    }}
                  />
                </Paper>
              </Box>

              <Typography
                variant="h5"
                align="center"
                gutterBottom
                color={
                  gameState.gameStatus === "success"
                    ? "success.main"
                    : gameState.gameStatus === "failed" ||
                      gameState.gameStatus === "timeout"
                    ? "error.main"
                    : "primary.main"
                }
                fontWeight="bold"
              >
                {gameState.gameStatus === "playing"
                  ? "Select all objects you can see in the image:"
                  : gameState.gameStatus === "success"
                  ? "Great job! You found all objects!"
                  : gameState.gameStatus === "timeout"
                  ? "Time's up! Try again!"
                  : "Sorry, you ran out of chances!"}
              </Typography>

              <Grid container spacing={2} sx={{ mt: 2 }}>
                {gameState.answerOptions.map((option, idx) => {
                  const isSelected = gameState.selectedAnswers.includes(option);
                  const isCorrect = gameState.objectsToFind.includes(option);
                  const showCorrect = gameState.gameStatus !== "playing";

                  let btnColor = "primary";
                  if (isSelected && isCorrect) btnColor = "success";
                  else if (isSelected && !isCorrect) btnColor = "error";
                  else if (showCorrect && isCorrect) btnColor = "success";

                  return (
                    <Grid item xs={6} sm={4} key={idx}>
                      <Button
                        onClick={() => handleAnswerSelect(option)}
                        variant={
                          isSelected || (showCorrect && isCorrect)
                            ? "contained"
                            : "outlined"
                        }
                        color={btnColor}
                        sx={{
                          width: "100%",
                          py: 1.5,
                          borderRadius: 3,
                          textTransform: "capitalize",
                          fontWeight: "bold",
                          fontSize: "1rem",
                          transition: "all 0.2s ease",
                        }}
                        disabled={
                          gameState.gameStatus !== "playing" || isSelected
                        }
                      >
                        {option}
                      </Button>
                    </Grid>
                  );
                })}
              </Grid>
            </>
          )}
        </CardContent>

        <CardActions sx={{ justifyContent: "center", pb: 3, pt: 1 }}>
          {gameState.gameStatus === "playing" && (
            <Button
              onClick={showHint}
              variant="outlined"
              color="warning"
              startIcon={<LightbulbIcon />}
              disabled={gameState.hint}
              sx={{ mr: 2, borderRadius: 3 }}
            >
              Hint
            </Button>
          )}

          {(gameState.gameStatus === "success" ||
            gameState.gameStatus === "failed" ||
            gameState.gameStatus === "timeout") && (
            <Button
              onClick={nextRound}
              variant="contained"
              color="primary"
              size="large"
              sx={{ px: 4, py: 1, borderRadius: 3 }}
            >
              Next Challenge
            </Button>
          )}
        </CardActions>
      </StyledCard>

      <Snackbar
        open={alert.open}
        autoHideDuration={3000}
        onClose={handleCloseAlert}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert onClose={handleCloseAlert} severity={alert.severity}>
          {alert.message}
        </Alert>
      </Snackbar>

      <Dialog open={dialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>
          {gameState.consecutiveSuccesses >= 3
            ? "Level Up!"
            : "Difficulty Adjusted"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {gameState.consecutiveSuccesses >= 3
              ? `Great job! You've been doing so well that we're increasing the difficulty to level ${gameState.difficulty}!`
              : `We've noticed you're finding this challenging, so we've adjusted the difficulty to make it more fun!`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="primary" autoFocus>
            Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ObjectRecognitionGame;