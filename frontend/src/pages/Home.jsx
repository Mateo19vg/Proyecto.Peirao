import React from "react"
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="text-center py-12">
      <h1 className="text-4xl font-bold text-ocean-900 mb-4">
        O Peirao
      </h1>
      <p className="text-lg text-gray-600 mb-10">
        Predice las mejores condiciones para pescar en tus spots favoritos.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-8">
        <FeatureCard
          to="/predictor"
          title="Predictor"
          desc="Consulta el tiempo y la puntuación de pesca en tiempo real"
        />
        <FeatureCard
          to="/log"
          title="Mis Capturas"
          desc="Revisa el historial de todas tus capturas registradas"
        />
        <FeatureCard
          to="/add"
          title="Registrar"
          desc="Anota una nueva captura con fotos y condiciones del momento"
        />
      </div>
    </div>
  )
}

function FeatureCard({ to, emoji, title, desc }) {
  return (
    <Link
      to={to}
      className="block bg-white rounded-2xl shadow-md p-6 hover:shadow-xl hover:-translate-y-1 transition-all border border-ocean-100"
    >
      <div className="text-4xl mb-3">{emoji}</div>
      <h2 className="text-lg font-semibold text-ocean-900 mb-1">{title}</h2>
      <p className="text-sm text-gray-500">{desc}</p>
    </Link>
  )
}
