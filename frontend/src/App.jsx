import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import MapPage from './components/MapPage';
import Login from './components/Login';
import Register from './components/Register';
import ProfilePage from './components/ProfilePage';
import GroupsPage from './components/GroupsPage';

const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    return token ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <MapPage />
            </ProtectedRoute>
          } />

          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />

          <Route path="/groups" element={
            <ProtectedRoute>
              <GroupsPage />
            </ProtectedRoute>
          } />

        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;