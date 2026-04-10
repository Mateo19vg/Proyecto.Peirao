import React from "react"
import { useState, useEffect } from 'react'
import { getSpots, getEspecies, getPrediccion } from '../services/api'

export default function Predictor() {
  const [spots, setSpots] = useState([])
  const [especies, setEspecies] = useState([])
  const [spotId, setSpotId] = useState('')
  const [especieId, setEspecieId] = useState('')
  const [resultado, setResultado] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Cargar datos iniciales al montar
  useEffect(() => {
    getSpots().then(setSpots)
    getEspecies().then(setEspecies)
  }, [])

  const handlePrediccion = async () => {
    if (!spotId || !especieId) return
    setLoading(true)
    setError(null)
    try {
      const data = await getPrediccion(spotId, especieId)
      setResultado(data)
    } catch {
      setError('Error al conectar con el servidor. ¿Está corriendo el backend?')
    } finally {
      setLoading(false)
    }
  }

  // Color de la barra según puntuación
  const barColor = resultado
    ? resultado.puntuacion >= 75 ? 'bg-green-500'
    : resultado.puntuacion >= 45 ? 'bg-yellow-400'
    : 'bg-red-500'
    : 'bg-gray-200'

  return (
    <div>
      <h1 className="text-2xl font-bold text-ocean-900 mb-6">🌊 Predictor de Pesca</h1>

      {/* Selector de spot y especie */}
      <div className="bg-white rounded-2xl shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Spot</label>
            <select
              className="w-full border rounded-lg p-2 text-sm"
              value={spotId}
              onChange={e => setSpotId(e.target.value)}
            >
              <option value="">Selecciona un spot...</option>
              {spots.map(s => (
                <option key={s.id} value={s.id}>{s.nombre} ({s.tipo})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Especie</label>
            <select
              className="w-full border rounded-lg p-2 text-sm"
              value={especieId}
              onChange={e => setEspecieId(e.target.value)}
            >
              <option value="">Selecciona una especie...</option>
              {especies.map(e => (
                <option key={e.id} value={e.id}>{e.nombre}</option>
              ))}
            </select>
          </div>
        </div>
        <button
          onClick={handlePrediccion}
          disabled={!spotId || !especieId || loading}
          className="w-full bg-ocean-700 text-white py-2 rounded-lg font-medium hover:bg-ocean-900 disabled:opacity-40 transition-colors"
        >
          {loading ? 'Consultando...' : '🎣 Ver predicción'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {error}
        </div>
      )}

      {/* Resultado */}
      {resultado && (
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="font-semibold text-ocean-900 mb-4 text-lg">
            {resultado.spot.nombre} · {resultado.especie.nombre}
          </h2>

          {/* Barra de puntuación */}
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-500">Puntuación</span>
              <span className="font-bold">{resultado.puntuacion}/100</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-3">
              <div
                className={`${barColor} h-3 rounded-full transition-all`}
                style={{ width: `${resultado.puntuacion}%` }}
              />
            </div>
          </div>

          <p className="text-gray-700 text-sm mb-4">{resultado.resumen}</p>

          {/* Detalles del tiempo */}
          {resultado.condiciones && (
            <div className="grid grid-cols-2 gap-3 text-sm">
              <Dato label="🌡️ Agua" value={`${resultado.condiciones.temperatura_agua?.toFixed(1)}°C`} />
              <Dato label="💨 Viento" value={`${resultado.condiciones.velocidad_viento?.toFixed(1)} km/h`} />
              <Dato label="🌊 Olas" value={`${resultado.condiciones.altura_olas?.toFixed(1)} m`} />
              <Dato label="☁️ Tiempo" value={resultado.descripcion_tiempo} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Dato({ label, value }) {
  return (
    <div className="bg-ocean-50 rounded-lg p-3">
      <div className="text-gray-500">{label}</div>
      <div className="font-semibold text-ocean-900">{value ?? '—'}</div>
    </div>
  )
}
