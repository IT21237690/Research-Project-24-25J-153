import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import Lobby from './pages/Lobby';
import Login from './pages/LoginPage';
import HomePage from './pages/HomePage';
import VideoPage from './pages/VideoPage';
import UserProfile from './pages/UserProfile';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import './App.css';

const App: React.FC = () => {
  return (
    <UserProvider>
      <Router>
        <Routes>
          {/* New Lobby route as the default landing page */}
          <Route path="/" element={<Lobby />} />
          
          <Route path="/login" element={<Login />} />
          
          <Route path="/home" element={
            <ProtectedRoute>
              <Layout>
                <HomePage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/video/:videoId" element={
            <ProtectedRoute>
              <Layout>
                <VideoPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/profile" element={
            <ProtectedRoute>
              <Layout>
                <UserProfile />
              </Layout>
            </ProtectedRoute>
          } />
          
          {/* Redirect unknown routes to the lobby */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </UserProvider>
  );
};

export default App;