import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Home, User, LogOut } from 'lucide-react';
import { useUser } from '../context/UserContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { username, logout } = useUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-blue-600">
            KidsTube
          </Link>

          <nav className="flex items-center space-x-4">
            <Link to="/home" className="flex items-center text-gray-600 hover:text-blue-600">
              <Home size={18} className="mr-1" /> Home
            </Link>
            <Link to="/profile" className="flex items-center text-gray-600 hover:text-blue-600">
              <User size={18} className="mr-1" /> Profile
            </Link>
            <button onClick={handleLogout} className="flex items-center text-gray-600 hover:text-red-600">
              <LogOut size={18} className="mr-1" /> Logout
            </button>
          </nav>
        </div>
      </header>

      <main className="container mx-auto py-6">
        {children}
      </main>

      <footer className="bg-white py-4 border-t">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          "Bringing joy, learning, and safe entertainment to every little explorer!" 🌟🎥
        </div>
      </footer>
    </div>
  );
};

export default Layout;