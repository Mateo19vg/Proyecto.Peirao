import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getPerfil, getMiPerfil, updatePerfil } from '../services/api'

export default function Perfil() {
  const { usuarioId } = useParams() // si existe, es perfil público de otro usuario
  const esPropio = !usuarioId

  const [perfil, setPerfil] = useState(null)
  const [bio, setBio] = useState('')
  const [mostrarNombre, setMostrarNombre] = useState(true)
  const [esPublico, setEsPublico] = useState(true)
  const [avatarFile, setAvatarFile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [guardando, setGuardando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const cargar = esPropio ? getMiPerfil() : getPerfil(usuarioId)
    cargar
      .then(data => {
        setPerfil(data)
        setBio(data.bio || '')
        setMostrarNombre(data.mostrar_nombre)
        setEsPublico(data.es_publico)
      })
      .catch((err) => {
        const msg = err.response?.data?.error || 'No se pudo cargar el perfil.'
        setError(msg)
      })
      .finally(() => setLoading(false))
  }, [usuarioId, esPropio])

  const handleGuardar = async () => {
    setGuardando(true); setError(''); setMensaje('')
    try {
      const form = new FormData()
      form.append('bio', bio)
      form.append('mostrar_nombre', mostrarNombre)
      form.append('es_publico', esPublico)
      if (avatarFile) form.append('avatar', avatarFile)
      const actualizado = await updatePerfil(form)
      setPerfil(actualizado)
      setMensaje('Perfil actualizado correctamente.')
    } catch (err) {
      setError('Error al guardar los cambios.')
    } finally {
      setGuardando(false)
    }
  }

  if (loading) return <div className="max-w-xl mx-auto p-8 text-center text-gray-400">Cargando perfil...</div>
  if (error && !perfil) return <div className="max-w-xl mx-auto p-8 text-center text-red-500">{error}</div>

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-ocean-900 mb-6">
        {esPropio ? 'Mi perfil' : `Perfil de ${perfil.username}`}
      </h1>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col gap-5">
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 rounded-full bg-gray-100 overflow-hidden flex items-center justify-center text-2xl text-gray-400 font-bold">
            {perfil.avatar_url
              ? <img src={perfil.avatar_url} alt="avatar" className="w-full h-full object-cover" />
              : (perfil.username?.[0]?.toUpperCase() || '?')}
          </div>
          <div>
            <p className="font-bold text-lg text-ocean-900">
              {esPropio || perfil.mostrar_nombre ? perfil.username : 'Pescador anónimo'}
            </p>
            {!esPropio && !perfil.mostrar_nombre && (
              <p className="text-xs text-gray-400 italic">Este pescador prefiere mantenerse en el anonimato</p>
            )}
          </div>
        </div>

        {esPropio ? (
          <>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Foto de perfil</label>
              <input type="file" accept="image/*" onChange={e => setAvatarFile(e.target.files[0] || null)}
                className="border border-gray-200 p-2.5 rounded-lg text-sm" />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Biografía</label>
              <textarea rows={3} maxLength={280} value={bio} onChange={e => setBio(e.target.value)}
                className="border border-gray-200 p-2.5 rounded-lg text-sm outline-none focus:border-blue-400 resize-none"
                placeholder="Cuéntanos algo sobre ti como pescador..." />
              <span className="text-xs text-gray-400 text-right">{bio.length}/280</span>
            </div>

            <label className="flex items-center gap-3 border border-gray-200 rounded-lg p-3 cursor-pointer select-none">
              <input type="checkbox" checked={esPublico} onChange={e => setEsPublico(e.target.checked)}
                className="accent-blue-600 w-4 h-4" />
              <div>
                <p className="text-sm font-semibold text-gray-700">Perfil público</p>
                <p className="text-xs text-gray-400">Si lo desactivas (perfil privado), solo tú podrás ver tus capturas y zonas de pesca, y tú tampoco podrás ver las de otros pescadores.</p>
              </div>
            </label>

            <label className="flex items-center gap-3 border border-gray-200 rounded-lg p-3 cursor-pointer select-none">
              <input type="checkbox" checked={mostrarNombre} onChange={e => setMostrarNombre(e.target.checked)}
                className="accent-blue-600 w-4 h-4" />
              <div>
                <p className="text-sm font-semibold text-gray-700">Mostrar mi nombre en mis capturas</p>
                <p className="text-xs text-gray-400">Si lo desactivas, tus capturas aparecerán como "Pescador anónimo" para los demás</p>
              </div>
            </label>

            <button onClick={handleGuardar} disabled={guardando}
              className="w-full bg-ocean-700 text-white py-3 rounded-lg text-sm font-semibold hover:bg-ocean-900 disabled:opacity-50 transition-all">
              {guardando ? 'Guardando...' : 'Guardar cambios'}
            </button>

            {mensaje && <p className="text-green-600 text-sm text-center">{mensaje}</p>}
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          </>
        ) : (
          perfil.bio && perfil.mostrar_nombre && (
            <p className="text-sm text-gray-600 italic border-l-2 border-blue-100 pl-3">{perfil.bio}</p>
          )
        )}
      </div>
    </div>
  )
}