import React from "react"
import { useState, useEffect, useCallback } from 'react'
import { getCapturas, deleteCaptura, getEspecies, getSpots } from '../services/api'

export default function Log() {
  const [data, setData] = useState({ count: 0, next: null, previous: null, results: [] })
  const [especies, setEspecies] = useState([])
  const [spots, setSpots] = useState([])

  const [filtroEspecie, setFiltroEspecie] = useState('')
  const [filtroSpot, setFiltroSpot] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [pagina, setPagina] = useState(1)

  useEffect(() => {
    getEspecies().then(setEspecies)
    getSpots().then(setSpots)
  }, [])

  const cargar = useCallback(() => {
    const filters = { page: pagina }
    if (filtroEspecie) filters.especie = filtroEspecie
    if (filtroSpot) filters.spot = filtroSpot
    if (busqueda) filters.search = busqueda
    getCapturas(filters).then(setData)
  }, [filtroEspecie, filtroSpot, busqueda, pagina])

  useEffect(() => { cargar() }, [cargar])

  const handleFiltro = (setter) => (e) => {
    setter(e.target.value)
    setPagina(1)
  }

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar esta captura?')) return
    await deleteCaptura(id)
    cargar()
  }

  const totalPaginas = Math.ceil(data.count / 10)

  return (
    <div>
      <h1 className="text-2xl font-bold text-ocean-900 mb-6">📋 Mis Capturas</h1>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6 space-y-3">
        <input
          type="text"
          placeholder="🔍 Buscar en notas..."
          value={busqueda}
          onChange={handleFiltro(setBusqueda)}
          className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ocean-500"
        />
        <div className="flex gap-3">
          <select className="border rounded-lg p-2 text-sm flex-1" value={filtroEspecie} onChange={handleFiltro(setFiltroEspecie)}>
            <option value="">Todas las especies</option>
            {especies.map(e => <option key={e.id} value={e.id}>{e.nombre}</option>)}
          </select>
          <select className="border rounded-lg p-2 text-sm flex-1" value={filtroSpot} onChange={handleFiltro(setFiltroSpot)}>
            <option value="">Todos los spots</option>
            {spots.map(s => <option key={s.id} value={s.id}>{s.nombre}</option>)}
          </select>
        </div>
      </div>

      <p className="text-sm text-gray-400 mb-3">
        {data.count} captura{data.count !== 1 ? 's' : ''} encontrada{data.count !== 1 ? 's' : ''}
      </p>

      {data.results.length === 0 ? (
        <p className="text-gray-400 text-center py-12">No hay capturas que coincidan.</p>
      ) : (
        <div className="space-y-4">
          {data.results.map(c => (
            <div key={c.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex justify-between items-start gap-4">
              <div className="flex-1">
                <div className="font-semibold text-ocean-900">{c.especie_nombre}</div>
                <div className="text-sm text-gray-500">{c.spot_nombre} · {c.fecha} {c.hora?.slice(0, 5)}</div>
                <div className="flex gap-3 mt-1">
                  {c.peso_kg && <span className="text-sm text-gray-600">⚖️ {c.peso_kg} kg</span>}
                  {c.longitud_cm && <span className="text-sm text-gray-600">📏 {c.longitud_cm} cm</span>}
                </div>
                {c.notas && <div className="text-sm text-gray-400 mt-1 italic">"{c.notas}"</div>}
              </div>
              {c.foto_url && (
                <img
                  src={c.foto_url}
                  alt="captura"
                  className="w-20 h-20 object-cover rounded-xl flex-shrink-0 cursor-pointer hover:opacity-90"
                  onClick={() => window.open(c.foto_url, '_blank')}
                />
              )}
              <button onClick={() => handleDelete(c.id)} className="text-red-400 hover:text-red-600 text-sm self-start">🗑️</button>
            </div>
          ))}
        </div>
      )}

      {totalPaginas > 1 && (
        <div className="flex items-center justify-center gap-3 mt-8">
          <button disabled={pagina === 1} onClick={() => setPagina(p => p - 1)} className="px-4 py-2 rounded-lg border text-sm disabled:opacity-30 hover:bg-ocean-50 transition">← Anterior</button>
          <span className="text-sm text-gray-500">Página {pagina} de {totalPaginas}</span>
          <button disabled={pagina === totalPaginas} onClick={() => setPagina(p => p + 1)} className="px-4 py-2 rounded-lg border text-sm disabled:opacity-30 hover:bg-ocean-50 transition">Siguiente →</button>
        </div>
      )}
    </div>
  )
}
