import React, { useState, useEffect } from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline,
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import { 
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  Person as PersonIcon,
  EmojiEvents as EmojiEventsIcon
} from '@mui/icons-material';
import ObjectRecognitionGame from './GamePage';
import api from './api';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [user, setUser] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [loginOpen, setLoginOpen] = useState(false);
  const [registerOpen, setRegisterOpen] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    email: "",
  });
  const [leaderboardOpen, setLeaderboardOpen] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        const response = await api.get("/auth/me");
        if (response.data.success) {
          setUser(response.data.user);
        localStorage.setItem("userId", response.data.user._id);

        }
      } catch (error) {
        console.log("Not authenticated");
      }
    };

    // Check for dark mode preference
    const savedMode = localStorage.getItem("darkMode");
    if (savedMode) {
      setDarkMode(savedMode === "true");
    } else {
      setDarkMode(window.matchMedia("(prefers-color-scheme: dark)").matches);
    }

    checkAuth();
  }, []);

  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light",
      primary: {
        main: "#3f51b5",
      },
      secondary: {
        main: "#f50057",
      },
      background: {
        default: darkMode ? "#121212" : "#f5f5f5",
        paper: darkMode ? "#1e1e1e" : "#ffffff",
      },
    },
    typography: {
      fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
      h4: {
        fontWeight: 700,
      },
      button: {
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontSize: "1rem",
          },
        },
      },
    },
  });

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    localStorage.setItem("darkMode", String(!darkMode));
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleOpenLogin = () => {
    handleClose();
    setLoginOpen(true);
  };

  const handleOpenRegister = () => {
    handleClose();
    setRegisterOpen(true);
  };

  const handleCloseDialogs = () => {
    setLoginOpen(false);
    setRegisterOpen(false);
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleLogin = async () => {
    try {
      const response = await api.post("/auth/login", {
        username: formData.username,
        password: formData.password,
      });

      if (response.data.success) {
        localStorage.setItem("token", response.data.token);
        setUser(response.data.user);
        console.log(response.data.user)
        handleCloseDialogs();
        // Refresh page to update game state
        window.location.reload();
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login failed. Please check your credentials.");
    }
  };

  const handleRegister = async () => {
    try {
      const response = await api.post(
        "/auth/register",
        {
          username: formData.username,
          password: formData.password,
          email: formData.email,
        },
        {
          withCredentials: true,
        }
      );

      if (response.data.success) {
        localStorage.setItem("token", response.data.token);
        setUser(response.data.user);
        handleCloseDialogs();
        // Refresh page to update game state
        window.location.reload();
      }
    } catch (error) {
      console.error("Registration failed:", error);
      alert("Registration failed. Please try a different username or email.");
    }
  };

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout");
      localStorage.removeItem("token");
      setUser(null);
      handleClose();
      // Refresh page to update game state
      window.location.reload();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await api.get("/game/leaderboard");
      if (response.data.success) {
        setLeaderboard(response.data.leaderboard);
        setLeaderboardOpen(true);
      }
    } catch (error) {
      console.error("Failed to fetch leaderboard:", error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          flexGrow: 1,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <AppBar position="static" color="primary" elevation={3}>
          <Toolbar>
            <Typography
              variant="h5"
              component="div"
              sx={{ flexGrow: 1, fontWeight: "bold" }}
            >
              Image Explorer
            </Typography>

            <IconButton color="inherit" onClick={toggleDarkMode} sx={{ mr: 1 }}>
              {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>

            <Button
              color="inherit"
              startIcon={<EmojiEventsIcon />}
              onClick={fetchLeaderboard}
              sx={{ mr: 2 }}
            >
              Leaderboard
            </Button>

            {user ? (
              <>
                <Button
                  startIcon={
                    <Avatar
                      sx={{ width: 30, height: 30, bgcolor: "secondary.main" }}
                    >
                      {user.username.charAt(0).toUpperCase()}
                    </Avatar>
                  }
                  onClick={handleMenu}
                  color="inherit"
                  sx={{ textTransform: "none" }}
                >
                  {user.username}
                </Button>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleClose}
                >
                  <MenuItem onClick={handleLogout}>Logout</MenuItem>
                </Menu>
              </>
            ) : (
              <>
                <IconButton size="large" onClick={handleMenu} color="inherit">
                  <PersonIcon />
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleClose}
                >
                  <MenuItem onClick={handleOpenLogin}>Login</MenuItem>
                  <MenuItem onClick={handleOpenRegister}>Register</MenuItem>
                </Menu>
              </>
            )}
          </Toolbar>
        </AppBar>

        <Box
          sx={{ flexGrow: 1, py: 2, display: "flex", flexDirection: "column" }}
        >
          <ObjectRecognitionGame />
        </Box>

        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: "auto",
            backgroundColor:
              theme.palette.mode === "light"
                ? theme.palette.grey[200]
                : theme.palette.grey[800],
          }}
        >
          <Container maxWidth="sm">
            <Typography variant="body2" color="text.secondary" align="center">
              © {new Date().getFullYear()} Image Explorer
            </Typography>
          </Container>
        </Box>
      </Box>

      {/* Login Dialog */}
      <Dialog open={loginOpen} onClose={handleCloseDialogs}>
        <DialogTitle>Login</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="username"
            label="Username"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.username}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            name="password"
            label="Password"
            type="password"
            fullWidth
            variant="outlined"
            value={formData.password}
            onChange={handleInputChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleLogin} variant="contained">
            Login
          </Button>
        </DialogActions>
      </Dialog>

      {/* Register Dialog */}
      <Dialog open={registerOpen} onClose={handleCloseDialogs}>
        <DialogTitle>Register</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="username"
            label="Username"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.username}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            name="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={formData.email}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            name="password"
            label="Password"
            type="password"
            fullWidth
            variant="outlined"
            value={formData.password}
            onChange={handleInputChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialogs}>Cancel</Button>
          <Button onClick={handleRegister} variant="contained">
            Register
          </Button>
        </DialogActions>
      </Dialog>

      {/* Leaderboard Dialog */}
      <Dialog
        open={leaderboardOpen}
        onClose={() => setLeaderboardOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Leaderboard</DialogTitle>
        <DialogContent>
          {leaderboard.length > 0 ? (
            <Box sx={{ width: "100%" }}>
              {leaderboard.map((entry, index) => (
                <Box
                  key={index}
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    p: 2,
                    borderBottom: "1px solid",
                    borderColor: "divider",
                    bgcolor:
                      index < 3
                        ? `rgba(${
                            index === 0
                              ? "255, 215, 0"
                              : index === 1
                              ? "192, 192, 192"
                              : "205, 127, 50"
                          }, 0.1)`
                        : "transparent",
                  }}
                >
                  <Box display="flex" alignItems="center">
                    <Typography
                      variant="h6"
                      sx={{ width: 30, fontWeight: "bold" }}
                    >
                      {index + 1}.
                    </Typography>
                    <Avatar
                      sx={{
                        bgcolor:
                          index < 3
                            ? ["gold", "silver", "#cd7f32"][index]
                            : "primary.main",
                        mr: 2,
                      }}
                    >
                      {entry.username.charAt(0).toUpperCase()}
                    </Avatar>
                    <Typography variant="body1">{entry.username}</Typography>
                  </Box>
                  <Typography
                    variant="h6"
                    fontWeight="bold"
                    color="primary.main"
                  >
                    {entry.highScore}
                  </Typography>
                </Box>
              ))}
            </Box>
          ) : (
            <Typography variant="body1" align="center" sx={{ py: 3 }}>
              No scores available yet. Be the first to set a high score!
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLeaderboardOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </ThemeProvider>
  );
}

export default App;