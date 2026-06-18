import React from "react"
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Predictor from './pages/Predictor'
import Log from './pages/Log'
import AddCaptura from './pages/AddCaptura'
import Login from './pages/Login';
import Register from './pages/Register';
import Perfil from './pages/Perfil';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen bg-ocean-50">
          <Navbar />
          <main className="w-full">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/predictor" element={<Predictor />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/log" element={<Log />} />
              <Route path="/add" element={<PrivateRoute><AddCaptura /></PrivateRoute>} />
              <Route path="/perfil" element={<PrivateRoute><Perfil /></PrivateRoute>} />
              <Route path="/perfil/:usuarioId" element={<Perfil />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}