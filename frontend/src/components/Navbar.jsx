import React, { useState } from "react"
import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const linksBase = [
  { to: '/', label: 'Inicio' },
  { to: '/predictor', label: 'Predictor' },
  { to: '/chat', label: 'SharkAI Chat' },
]

const linksAuth = [
  { to: '/log', label: 'Mis Capturas' },
  { to: '/add', label: 'Registrar' },
]

export default function Navbar() {
  const { isAuth, logout } = useAuth()
  const [open, setOpen] = useState(false)

  const links = isAuth ? [...linksBase, ...linksAuth] : linksBase

  return (
    <nav className="bg-ocean-900 text-white shadow-lg">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between relative">
        <Link to="/" className="text-xl font-bold tracking-tight">O Peirao</Link>

        <div className="flex items-center gap-4">
          {links.map(link => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) =>
                `text-sm font-medium px-3 py-1 rounded transition-colors ${
                  isActive ? 'bg-ocean-500 text-white' : 'text-ocean-50 hover:bg-ocean-700'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}

          {/* Icono de usuario */}
          <div className="relative">
            <button
              onClick={() => setOpen(o => !o)}
              className="w-9 h-9 flex items-center justify-center rounded-full bg-ocean-700 hover:bg-ocean-500 transition-colors"
              aria-label="Cuenta"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                <path d="M12 12c2.7 0 4.9-2.2 4.9-4.9S14.7 2.2 12 2.2 7.1 4.4 7.1 7.1 9.3 12 12 12zm0 2.2c-3.3 0-9.8 1.6-9.8 4.9v2.7h19.6v-2.7c0-3.3-6.5-4.9-9.8-4.9z"/>
              </svg>
            </button>

            {open && (
              <div className="absolute right-0 mt-2 w-48 bg-white text-gray-800 rounded-lg shadow-lg overflow-hidden z-50">
                {isAuth ? (
                  <>
                    <Link
                      to="/perfil"
                      onClick={() => setOpen(false)}
                      className="block px-4 py-3 text-sm hover:bg-gray-100 border-b border-gray-100"
                    >
                      Mi perfil
                    </Link>
                    <button
                      onClick={() => { setOpen(false); logout() }}
                      className="w-full text-left px-4 py-3 text-sm hover:bg-gray-100"
                    >
                      Cerrar sesión
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      onClick={() => setOpen(false)}
                      className="block px-4 py-3 text-sm hover:bg-gray-100 border-b border-gray-100"
                    >
                      Iniciar sesión
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setOpen(false)}
                      className="block px-4 py-3 text-sm hover:bg-gray-100"
                    >
                      Registrarse
                    </Link>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}