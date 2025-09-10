import { Route, Routes } from "react-router-dom";

import './App.css';
import AuthRedirectRoute from './components/AuthRedirectRoute';
import Layout from './components/Layout';
import Cryptocurrency from './pages/Cryptocurrency';
import Dashboard from './pages/Dashboard';
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import News from './pages/News';
import ProfileEdit from './pages/ProfileEdit';
import SignupFlow from './pages/SignupFlow';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route
          index
          element={
            <AuthRedirectRoute>
              <Dashboard />
            </AuthRedirectRoute>
          }
        />
        <Route
          path="cryptocurrency/:id"
          element={
            <AuthRedirectRoute>
              <Cryptocurrency />
            </AuthRedirectRoute>
          }
        />
        <Route
          path="profile"
          element={
            <AuthRedirectRoute>
              <ProfileEdit />
            </AuthRedirectRoute>
          }
        />
        <Route path="news" element={<AuthRedirectRoute><News /></AuthRedirectRoute>} />
      </Route>
      <Route
        path="/signup"
        element={
          <AuthRedirectRoute>
            <SignupFlow />
          </AuthRedirectRoute>
        }
      />
      <Route
        path="/login"
        element={
          <AuthRedirectRoute>
            <Login />
          </AuthRedirectRoute>
        }
      />
      <Route path="/landing" element={<LandingPage />} />
    </Routes>
  );
}
export default App;
