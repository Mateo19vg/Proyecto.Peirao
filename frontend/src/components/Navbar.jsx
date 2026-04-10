import React from "react"
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: '🏠 Inicio' },
  { to: '/predictor', label: '🎣 Predictor' },
  { to: '/log', label: '📋 Mis Capturas' },
  { to: '/add', label: '➕ Registrar' },
]

export default function Navbar() {
  return (
    <nav className="bg-ocean-900 text-white shadow-lg">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <span className="text-xl font-bold tracking-tight">🐟 FishingPredictor</span>
        <div className="flex gap-4">
          {links.map(link => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) =>
                `text-sm font-medium px-3 py-1 rounded transition-colors ${
                  isActive
                    ? 'bg-ocean-500 text-white'
                    : 'text-ocean-50 hover:bg-ocean-700'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
