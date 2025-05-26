import React, { createContext, useState, useEffect, useContext } from 'react';

interface UserContextType {
  username: string;
  isLoggedIn: boolean;
  login: (username: string, age: number, interests: string[]) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [username, setUsername] = useState<string>('');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  // Check if user is already logged in on mount
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
      setUsername(storedUsername);
      setIsLoggedIn(true);
    }
  }, []);

  const login = (username: string, age: number, interests: string[]) => {
    localStorage.setItem('username', username);
    localStorage.setItem('age', age.toString());
    localStorage.setItem('interests', interests.join(','));
    setUsername(username);
    setIsLoggedIn(true);
  };

  const logout = () => {
    localStorage.removeItem('username');
    localStorage.removeItem('age');
    localStorage.removeItem('interests');
    setUsername('');
    setIsLoggedIn(false);
  };

  return (
    <UserContext.Provider value={{ username, isLoggedIn, login, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};