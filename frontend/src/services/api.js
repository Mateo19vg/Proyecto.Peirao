import axios from 'axios'

// Creamos la instancia centralizada de Axios
const API = axios.create({ baseURL: '/api' })

// ---------------------------------------------------------------------------
// INTERCEPTORES PARA SEGURIDAD JWT (Multiusuario Seguro)
// ---------------------------------------------------------------------------

// 1. Inyectar automáticamente el Token de Acceso en cada petición HTTP
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config;
  },
  (error) => Promise.reject(error)
)

// 2. Detectar Tokens caducados (401) y auto-renovarlos con el Refresh Token
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Si la API dice "No autorizado" (401) y no es un reintento previo
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          // Llamamos al endpoint de refresco usando axios plano (para no meter bucles infinitos)
          const response = await axios.post('/api/token/refresh/', { refresh: refreshToken })
          const newAccess = response.data.access

          // Guardamos el nuevo access token de corta duración
          localStorage.setItem('access_token', newAccess)

          // Modificamos la cabecera de la petición que falló y la relanzamos
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
          return API(originalRequest)
        } catch (refreshError) {
          // Si el refresh token también expiró, limpiamos sesión y mandamos al Login
          localStorage.clear()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }
    return Promise.reject(error)
  }
)

// ---------------------------------------------------------------------------
// ENDPOINTS DE AUTENTICACIÓN
// ---------------------------------------------------------------------------

export const login = async (username, password) => {
  const response = await API.post('/token/', { username, password })
  if (response.data.access) {
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    localStorage.setItem('username', username)
  }
  return response.data
}

// ¡NUEVO: Añadida la función que le faltaba a Register.jsx!
export const register = (username, password, email) => {
  return API.post('/register/', { username, password, email }).then(r => r.data)
}

export const logout = () => {
  localStorage.clear()
  window.location.href = '/'
}

// Comprueba si hay una sesión activa (usado por AuthContext / PrivateRoute)
export const isAuthenticated = () => !!localStorage.getItem('access_token')

// ---------------------------------------------------------------------------
// ENDPOINTS DE TU APLICACIÓN (Manteniendo tu lógica original)
// ---------------------------------------------------------------------------

export const getEspecies   = ()       => API.get('/especies/').then(r => r.data)
export const getSpots      = ()       => API.get('/spots/').then(r => r.data)
export const createSpot    = (spot)   => API.post('/spots/', spot).then(r => r.data)

// --- Perfil ---
export const getMiPerfil   = ()       => API.get('/perfil/').then(r => r.data)
export const getPerfil     = (usuarioId) => API.get(`/perfil/${usuarioId}/`).then(r => r.data)
export const updatePerfil  = (formData) => API.put('/perfil/', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
}).then(r => r.data)

export const enviarMensajeChat = (chatData) => API.post('/chat/', chatData).then(r => r.data)

export const getCapturas   = (params) => API.get('/capturas/', { params }).then(r => r.data)

export const createCaptura = (form)   => {
  const data = new FormData()
  Object.entries(form).forEach(([k, v]) => { 
    if (v !== null && v !== '') data.append(k, v) 
  })
  return API.post('/capturas/', data, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
}

export const deleteCaptura = (id)     => API.delete(`/capturas/${id}/`).then(r => r.data)

/**
 * getPrediccion — dos modos (Ahora retorna la serie de 15 días por horas):
 * Spot guardado:  getPrediccion(spotId, especieId)
 * Punto libre:    getPrediccion(null, especieId, lat, lon)
 */
export const getPrediccion = (spotId, especieId, lat = null, lon = null) => {
  const params = { especie_id: especieId }
  if (spotId) {
    params.spot_id = spotId
  } else if (lat !== null && lon !== null) {
    params.lat = lat
    params.lon = lon
  }
  return API.get('/prediccion/', { params }).then(r => r.data)
}

export default API;