import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Navigation2, MapPin, ShieldCheck, BarChart2,
  Clock, Loader2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { haversine } from '../utils/geo';

const API = 'http://localhost:8000';

// ─── Skeleton bar ────────────────────────────────────────────
const Skel = ({ w = '60px', h = '24px' }) => (
  <div className="skeleton" style={{ width: w, height: h }} />
);

// ─── Format helpers ──────────────────────────────────────────
const fmtK = (n) => {
  if (n == null) return '--';
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);
};

const fmtPct = (resumen) => {
  if (resumen?.puntualidad_percent != null) return resumen.puntualidad_percent;
  return '--';
};

const todayES = () => {
  const d = new Date();
  return d.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
};

const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1);

// ─── Sub-components ──────────────────────────────────────────

function StatBlock({ value, label, loading }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
      {loading
        ? <Skel w="48px" h="28px" />
        : <span style={{ fontSize: '26px', fontWeight: 700, letterSpacing: '-1px', color: 'var(--apple-label)', lineHeight: 1 }}>{value}</span>
      }
      <span style={{ fontSize: '10px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.8px', color: 'var(--apple-label-2)' }}>
        {label}
      </span>
    </div>
  );
}

function FreqRow({ parada, loading, separator }) {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: separator ? '10px' : 0 }}>
        {loading
          ? <Skel w="120px" h="16px" />
          : <span
              title={parada?.nombre_parada ?? ''}
              style={{
                fontSize: '13px',
                color: 'var(--apple-label)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                maxWidth: '200px',
                cursor: 'default',
              }}
            >
              {parada?.nombre_parada ?? '--'}
            </span>
        }
        {loading
          ? <Skel w="36px" h="20px" />
          : <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--apple-label)', letterSpacing: '-0.5px', flexShrink: 0, marginLeft: '8px' }}>
              {parada ? `${Math.round(parada.frecuencia_min)}m` : '--'}
            </span>
        }
      </div>
      {separator && <div style={{ height: '1px', backgroundColor: 'var(--apple-separator)', margin: '0 0 10px' }} />}
    </>
  );
}

// ─── Card wrappers ───────────────────────────────────────────

const CardLink = ({ to, children, style }) => (
  <Link
    to={to}
    className="apple-card"
    style={{
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--apple-surface)',
      borderRadius: 'var(--apple-radius)',
      padding: '20px',
      textDecoration: 'none',
      color: 'inherit',
      cursor: 'pointer',
      ...style
    }}
  >
    {children}
  </Link>
);

const CtaLabel = ({ children, color = 'var(--apple-blue)' }) => (
  <div
    className="cta-label"
    style={{
      marginTop: 'auto',
      paddingTop: '12px',
      fontSize: '12px',
      fontWeight: 600,
      color,
      letterSpacing: '0.3px',
    }}
  >
    {children}
  </div>
);

const CardIconRow = ({ icon: Icon, color, right }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
    <Icon size={20} color={color} strokeWidth={2} />
    {right}
  </div>
);

// ─── Main Component ──────────────────────────────────────────

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [resumen, setResumen] = useState(null);
  const [calificaciones, setCalificaciones] = useState([]);
  const [frecuencia, setFrecuencia] = useState([]);
  const [loading, setLoading] = useState(true);

  const [detectedStop, setDetectedStop] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [resRes, frecRes, calRes] = await Promise.all([
          fetch(`${API}/api/estadisticas/resumen`),
          fetch(`${API}/api/estadisticas/frecuencia`),
          fetch(`${API}/api/estadisticas/calificaciones`),
        ]);
        if (resRes.ok) setResumen(await resRes.json());
        if (frecRes.ok) setFrecuencia(await frecRes.json());
        if (calRes.ok) setCalificaciones(await calRes.json());
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const detectLocation = () => {
    if (!navigator.geolocation) return;
    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
          const res = await fetch(`${API}/api/paradas/todas`);
          const paradas = await res.json();
          let closest = null, minDist = Infinity;
          paradas.forEach(p => {
            const d = haversine(latitude, longitude, parseFloat(p.latitud), parseFloat(p.longitud));
            if (d < minDist) { minDist = d; closest = p; }
          });
          if (closest && minDist <= 200) setDetectedStop(closest);
        } catch { /* silent */ }
        finally { setGpsLoading(false); }
      },
      () => setGpsLoading(false)
    );
  };

  const pct = fmtPct(resumen);
  const registros = fmtK(resumen?.total_registros_horario);
  const rutasCount = loading ? null : (resumen?.total_rutas_activas ?? '--');
  const topFrec = frecuencia.slice(0, 2);

  return (
    <div style={{ backgroundColor: 'var(--apple-bg)', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '24px 20px 48px' }}>

        {/* ─── Header ─────────────────────────────────── */}
        <header style={{ marginBottom: '28px' }}>
          <h1
            className="greeting-heading"
            style={{ fontSize: '28px', color: 'var(--apple-label)' }}
          >
            Hola,{' '}
          <span style={{ color: 'var(--orange-accent)' }}>
            {user?.nombre?.split(' ')[0] || 'Estudiante'}
          </span>
          </h1>
          <p style={{ marginTop: '6px', fontSize: '14px', color: 'var(--apple-label-2)', fontWeight: 400 }}>
            {capitalize(todayES())}
            {' · '}
            {loading
              ? 'Cargando rutas...'
              : `${rutasCount} rutas activas ahora mismo`
            }
          </p>
        </header>

        {/* ─── Top Cards Grid (3 col) ──────────────── */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px',
          marginBottom: '12px',
        }}
          className="cards-top"
        >

          {/* CARD 1 — GPS Hero ──────────────────────── */}
          <div
            className="apple-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              background: 'var(--apple-label)',
              borderRadius: 'var(--apple-radius)',
              padding: '24px',
              cursor: 'pointer',
            }}
          >
            <Navigation2 size={20} color="var(--orange-accent)" strokeWidth={2} style={{ marginBottom: '12px' }} />
            <div style={{ fontSize: '17px', fontWeight: 600, color: 'var(--apple-bg)', letterSpacing: '-0.3px', marginBottom: '4px' }}>
              Detección GPS
            </div>
            <div style={{ fontSize: '13px', color: 'var(--apple-label-3)', lineHeight: 1.5, flexGrow: 1 }}>
              {detectedStop
                ? `📍 ${detectedStop.nombre_parada}`
                : 'Localiza tu parada más cercana'
              }
            </div>
            <button
              onClick={detectLocation}
              disabled={gpsLoading}
              style={{
                marginTop: '16px',
                background: 'var(--orange-accent)',
                color: '#ffffff',
                border: 'none',
                borderRadius: '980px',
                padding: '10px 20px',
                fontSize: '14px',
                fontWeight: 600,
                width: 'fit-content',
                opacity: gpsLoading ? 0.7 : 1,
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              {gpsLoading && <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />}
              {gpsLoading ? 'Localizando…' : detectedStop ? 'Verificado ✓' : 'Activar GPS'}
            </button>
          </div>

          {/* CARD 2 — Rutas Activas ─────────────────── */}
          <CardLink to="/mapa" style={{ position: 'relative' }}>
            <CardIconRow
              icon={MapPin}
              color="var(--apple-blue)"
              right={
                <div className="pulse-dot" style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--apple-green)' }} />
              }
            />
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--apple-label)', letterSpacing: '-0.2px' }}>
              Rutas Activas
            </div>
            <div style={{ fontSize: '12px', color: 'var(--apple-label-2)', marginTop: '4px', lineHeight: 1.5, flexGrow: 1 }}>
              Mapa interactivo de movilidad al CUT
            </div>
            <CtaLabel>EXPLORAR ›</CtaLabel>
          </CardLink>

          {/* CARD 3 — Seguridad ─────────────────────── */}
          <CardLink to="/incidentes">
            <CardIconRow icon={ShieldCheck} color="var(--apple-green)" />
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--apple-label)', letterSpacing: '-0.2px' }}>
              Seguridad
            </div>
            <div style={{ fontSize: '12px', color: 'var(--apple-label-2)', marginTop: '4px', lineHeight: 1.5, flexGrow: 1 }}>
              Reportes anónimos de incidentes en ruta
            </div>
            <CtaLabel>REPORTAR ›</CtaLabel>
          </CardLink>
        </div>

        {/* ─── Bottom Cards Grid (2 col) ───────────── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}
          className="cards-bottom"
        >

          {/* CARD 4 — Análisis ──────────────────────── */}
          <CardLink to="/dashboard">
            <CardIconRow icon={BarChart2} color="var(--orange-accent)" />
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--apple-label)', letterSpacing: '-0.2px' }}>
              Análisis
            </div>
            <div style={{ fontSize: '12px', color: 'var(--apple-label-2)', marginTop: '4px', lineHeight: 1.5 }}>
              Puntualidad y flujo de rutas
            </div>

            <div style={{ display: 'flex', gap: '20px', marginTop: '16px' }}>
              <StatBlock value={pct !== '--' ? `${pct}%` : '--'} label="Puntualidad" loading={loading} />
              <StatBlock value={registros} label="Registros" loading={loading} />
            </div>

            <CtaLabel>VER PANEL ›</CtaLabel>
          </CardLink>

          {/* CARD 5 — Frecuencia ────────────────────── */}
          <CardLink to="/horarios">
            <CardIconRow
              icon={Clock}
              color="var(--orange-accent)"
              right={loading && <Loader2 size={14} color="var(--apple-label-2)" style={{ animation: 'spin 1s linear infinite' }} />}
            />
            <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--apple-label)', letterSpacing: '-0.2px' }}>
              Frecuencia
            </div>
            <div style={{ fontSize: '12px', color: 'var(--apple-label-2)', marginTop: '4px', lineHeight: 1.5 }}>
              Intervalo promedio por ruta
            </div>

            <div style={{ marginTop: '16px', flexGrow: 1 }}>
              <FreqRow parada={topFrec[0]} loading={loading} separator={topFrec.length > 1} />
              <FreqRow parada={topFrec[1]} loading={loading} separator={false} />
            </div>

            <div style={{ fontSize: '9px', color: 'var(--apple-label-3)', marginTop: '4px', letterSpacing: '0.2px' }}>
              Frec. promedio · no es predicción en tiempo real
            </div>
            <CtaLabel>VER HORARIOS ›</CtaLabel>
          </CardLink>
        </div>

      </div>

      {/* ─── Spin animation ─────────────────────────── */}
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @media (max-width: 767px) {
          .cards-top { grid-template-columns: repeat(2, 1fr) !important; }
          .cards-bottom { grid-template-columns: 1fr 1fr !important; }
        }
        @media (max-width: 479px) {
          .cards-top { grid-template-columns: 1fr !important; }
          .cards-bottom { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
