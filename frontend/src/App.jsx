import React from "react"
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Predictor from './pages/Predictor'
import Log from './pages/Log'
import AddCaptura from './pages/AddCaptura'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-ocean-50">
        <Navbar />
        <main className="w-full">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/predictor" element={<Predictor />} />
            <Route path="/log" element={<Log />} />
            <Route path="/add" element={<AddCaptura />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}