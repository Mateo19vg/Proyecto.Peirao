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
        <main className="max-w-4xl mx-auto px-4 py-8">
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
