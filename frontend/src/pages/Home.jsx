import React, { useEffect, useState } from "react"
import { Link } from 'react-router-dom'

const NAV_ITEMS = [
  {
    to: "/predictor",
    label: "Predictor",
    number: "01",
    desc: "Consulta la puntuación de pesca en tiempo real combinando temperatura del agua, viento y condiciones meteorológicas para cada especie y spot.",
  },
  {
    to: "/log",
    label: "Diario",
    number: "02",
    desc: "Accede al historial completo de tus capturas. Filtra por especie o zona y visualiza tus registros sobre el mapa de Galicia.",
  },
  {
    to: "/add",
    label: "Registrar",
    number: "03",
    desc: "Anota una nueva captura con especie, ubicación GPS, peso, medida y foto. Los puntos personalizados se crean directamente sobre el mapa.",
  },
]

export default function Home() {
  const [visible, setVisible] = useState(false)
  useEffect(() => { const t = setTimeout(() => setVisible(true), 80); return () => clearTimeout(t) }, [])

  return (
    <div
      style={{
        fontFamily: "'Georgia', 'Times New Roman', serif",
        minHeight: "100vh",
        background: "#f7f5f0",
        color: "#1a1a1a",
      }}
    >
      {/* Hero */}
      <section
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "80px 32px 64px",
          opacity: visible ? 1 : 0,
          transform: visible ? "translateY(0)" : "translateY(18px)",
          transition: "opacity 0.7s ease, transform 0.7s ease",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-end", gap: 16, marginBottom: 8 }}>
          <span style={{ fontSize: 13, letterSpacing: "0.18em", color: "#6b7280", textTransform: "uppercase", fontFamily: "system-ui, sans-serif", fontWeight: 500 }}>
            Proyecto Intermodular · DAW2 · 2026
          </span>
        </div>

        <h1
          style={{
            fontSize: "clamp(52px, 9vw, 110px)",
            fontWeight: 400,
            lineHeight: 0.95,
            letterSpacing: "-0.03em",
            margin: "0 0 32px",
            color: "#0f2a3f",
          }}
        >
          O Peirao
        </h1>

        <div style={{ display: "flex", alignItems: "flex-start", gap: 48, flexWrap: "wrap" }}>
          <p
            style={{
              fontSize: 20,
              lineHeight: 1.65,
              color: "#374151",
              maxWidth: 520,
              margin: 0,
              fontStyle: "italic",
            }}
          >
            "O Peirao" — el muelle en gallego — es el punto de partida de toda jornada de pesca. Esta aplicación une datos meteorológicos en tiempo real con el conocimiento sobre cada especie para ayudar al pescador a tomar mejores decisiones.
          </p>

          <div style={{ flex: 1, minWidth: 220 }}>
            <div style={{ height: 1, background: "#d1c9b8", marginBottom: 20 }} />
            <p style={{ fontSize: 13, color: "#6b7280", fontFamily: "system-ui, sans-serif", lineHeight: 1.7, margin: 0 }}>
              Desarrollado por<br />
              <strong style={{ color: "#1a1a1a", fontSize: 15 }}>Mateo Varela García</strong><br />
              Centro de F.P. Afundación<br />
              Desarrollo de Aplicaciones Web — 2º curso
            </p>
          </div>
        </div>
      </section>

      {/* Divisor */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 32px" }}>
        <div style={{ height: 1, background: "#d1c9b8" }} />
      </div>

      {/* Secciones de navegación */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "0 32px 80px" }}>
        {NAV_ITEMS.map((item, i) => (
          <Link
            key={item.to}
            to={item.to}
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "64px 1fr auto",
                alignItems: "center",
                gap: 32,
                padding: "36px 0",
                borderBottom: "1px solid #e5dfd3",
                opacity: visible ? 1 : 0,
                transform: visible ? "translateX(0)" : "translateX(-12px)",
                transition: `opacity 0.6s ease ${0.2 + i * 0.12}s, transform 0.6s ease ${0.2 + i * 0.12}s`,
                cursor: "pointer",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = "#eeece7"
                e.currentTarget.style.marginLeft = "-32px"
                e.currentTarget.style.paddingLeft = "32px"
                e.currentTarget.style.marginRight = "-32px"
                e.currentTarget.style.paddingRight = "32px"
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = "transparent"
                e.currentTarget.style.marginLeft = "0"
                e.currentTarget.style.paddingLeft = "0"
                e.currentTarget.style.marginRight = "0"
                e.currentTarget.style.paddingRight = "0"
              }}
            >
              <span style={{ fontSize: 13, color: "#9ca3af", fontFamily: "system-ui, sans-serif", letterSpacing: "0.1em" }}>
                {item.number}
              </span>
              <div>
                <h2 style={{ fontSize: 28, fontWeight: 400, margin: "0 0 6px", color: "#0f2a3f", letterSpacing: "-0.02em" }}>
                  {item.label}
                </h2>
                <p style={{ fontSize: 14, color: "#6b7280", margin: 0, fontFamily: "system-ui, sans-serif", lineHeight: 1.6, maxWidth: 480 }}>
                  {item.desc}
                </p>
              </div>
              <span style={{ fontSize: 22, color: "#9ca3af", fontFamily: "system-ui, sans-serif" }}>→</span>
            </div>
          </Link>
        ))}
      </section>

      {/* Stack tecnológico */}
      <section
        style={{
          background: "#0f2a3f",
          color: "#f7f5f0",
          padding: "56px 32px",
          opacity: visible ? 1 : 0,
          transition: "opacity 0.8s ease 0.6s",
        }}
      >
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <p style={{ fontSize: 11, letterSpacing: "0.18em", color: "#6b9ab8", textTransform: "uppercase", fontFamily: "system-ui, sans-serif", marginBottom: 32 }}>
            Stack tecnológico
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "12px 40px" }}>
            {["Django · Django REST Framework", "React 18 · Vite · Tailwind CSS", "Open-Meteo API (meteorología marina)", "Leaflet · React-Leaflet (cartografía)", "SQLite · Axios · React Router v6"].map(t => (
              <span key={t} style={{ fontSize: 14, color: "#cbd5e1", fontFamily: "system-ui, sans-serif" }}>{t}</span>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}