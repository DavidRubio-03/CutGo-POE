import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, Navigation, MapPin, CheckCircle, Loader2, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { haversine } from '../utils/geo';

export default function RegistroHorario() {
  const { user } = useAuth();
  const [rutas, setRutas] = useState([]);
  const [paradas, setParadas] = useState([]);
  const [selectedRuta, setSelectedRuta] = useState('');
  const [selectedParada, setSelectedParada] = useState('');
  const [estimation, setEstimation] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showToast, setShowToast] = useState(false);
  
  // GPS State
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsMessage, setGpsMessage] = useState({ text: '', type: '' });
  const [locationVerified, setLocationVerified] = useState(false);

  const handleDetectStop = () => {
    if (!navigator.geolocation) {
      setGpsMessage({ text: 'Geolocalización no soportada.', type: 'error' });
      return;
    }

    setGpsLoading(true);
    setGpsMessage({ text: 'Obteniendo ubicación...', type: 'info' });

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          const res = await fetch('http://localhost:8000/api/paradas/todas');
          const allParadas = await res.json();
          
          let closestStop = null;
          let minDistance = Infinity;

          allParadas.forEach(stop => {
            const distance = haversine(latitude, longitude, parseFloat(stop.latitud), parseFloat(stop.longitud));
            if (distance < minDistance) {
              minDistance = distance;
              closestStop = stop;
            }
          });

          if (closestStop && minDistance <= 200) {
            setSelectedRuta(closestStop.id_ruta.toString());
            setSelectedParada(closestStop.id_parada.toString());
            setLocationVerified(true);
            setGpsMessage({ 
              text: `Detectamos que estás cerca de ${closestStop.nombre_parada}`, 
              type: 'success' 
            });
          } else {
            setLocationVerified(false);
            setGpsMessage({ 
              text: 'No encontramos una parada cercana. ¿Estás en la ruta correcta?', 
              type: 'error' 
            });
          }
        } catch (err) {
          console.error(err);
          setGpsMessage({ text: 'Error al conectar con el servidor.', type: 'error' });
        } finally {
          setGpsLoading(false);
          setTimeout(() => setGpsMessage({ text: '', type: '' }), 5000);
        }
      },
      (error) => {
        setGpsLoading(false);
        setGpsMessage({ text: 'Permiso de ubicación denegado.', type: 'error' });
        setTimeout(() => setGpsMessage({ text: '', type: '' }), 4000);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  useEffect(() => {
    fetch('http://localhost:8000/api/rutas')
      .then(res => res.json())
      .then(data => setRutas(data));
  }, []);

  useEffect(() => {
    if (selectedRuta) {
      fetch(`http://localhost:8000/api/rutas/${selectedRuta}/paradas`)
        .then(res => res.json())
        .then(data => setParadas(data));
    } else {
      setParadas([]);
      setSelectedParada('');
    }
  }, [selectedRuta]);

  useEffect(() => {
    if (selectedParada) {
      setLoading(true);
      fetch(`http://localhost:8000/api/paradas/${selectedParada}/proximos`)
        .then(res => res.json())
        .then(data => {
          setEstimation(data);
          setHistory(data.recent_records || []);
          setLoading(false);
        });
    }
  }, [selectedParada]);

  const handleRegister = async () => {
    if (!selectedParada || !user) return;
    setSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/api/horarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_parada: parseInt(selectedParada),
          id_usuario: user.id_usuario,
          timestamp_real: new Date().toISOString()
        })
      });

      if (response.ok) {
        setShowToast(true);
        setTimeout(() => setShowToast(false), 3000);
        const res = await fetch(`http://localhost:8000/api/paradas/${selectedParada}/proximos`);
        const data = await res.json();
        setEstimation(data);
        setHistory(data.recent_records || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) return <Navigate to="/login" />;

  return (
    <div style={{ padding: '40px 24px', maxWidth: '600px', margin: '0 auto' }}>
      <header style={{ marginBottom: '48px' }}>
        <h2 style={{ fontSize: '36px', fontWeight: 900, marginBottom: '8px', letterSpacing: '-0.04em', lineHeight: 1.1 }}>Registro Horario</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '15px', fontWeight: 300 }}>Contribuye a la puntualidad de la comunidad.</p>
      </header>

      <div className="glass-card" style={{ padding: '32px', marginBottom: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <label className="text-xs-uppercase" style={{ display: 'block', marginBottom: '10px' }}>Seleccionar Ruta</label>
          <select 
            value={selectedRuta}
            onChange={(e) => setSelectedRuta(e.target.value)}
            style={{ width: '100%', padding: '16px', borderRadius: '16px', border: '1px solid var(--border)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px' }}
          >
            <option value="">Buscar ruta...</option>
            {rutas.map(r => <option key={r.id_ruta} value={r.id_ruta}>{r.nombre_ruta}</option>)}
          </select>
        </div>

        <div style={{ marginBottom: '32px' }}>
          <label className="text-xs-uppercase" style={{ display: 'block', marginBottom: '10px' }}>Parada</label>
          <select 
            value={selectedParada}
            onChange={(e) => setSelectedParada(e.target.value)}
            disabled={!selectedRuta}
            style={{ width: '100%', padding: '16px', borderRadius: '16px', border: '1px solid var(--border)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px', opacity: !selectedRuta ? 0.5 : 1 }}
          >
            <option value="">Seleccionar parada...</option>
            {paradas.map(p => <option key={p.id_parada} value={p.id_parada}>{p.nombre_parada}</option>)}
          </select>
        </div>

        <div style={{ textAlign: 'center' }}>
          <div className="text-xs-uppercase" style={{ marginBottom: '24px', opacity: 0.3 }}>— o —</div>
          <button 
            onClick={handleDetectStop}
            disabled={gpsLoading}
            style={{ 
              width: '100%', border: '1px solid var(--accent)', color: 'var(--accent)', 
              background: 'transparent', borderRadius: '50px', padding: '14px' 
            }}
          >
            {gpsLoading ? <Loader2 size={18} className="spinner-icon" /> : 'Detectar parada automáticamente'}
          </button>
          
          {locationVerified && (
            <div style={{ marginTop: '20px', color: 'var(--safe-green)', fontSize: '13px', fontWeight: 600, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
              <ShieldCheck size={18} /> GPS Verified
            </div>
          )}

          {gpsMessage.text && (
            <p style={{ marginTop: '16px', fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic', fontWeight: 300 }}>
              {gpsMessage.text}
            </p>
          )}
        </div>
      </div>

      {selectedParada && (
        <button 
          onClick={handleRegister}
          disabled={submitting}
          style={{ 
            width: '100%', backgroundColor: 'var(--text-main)', color: 'var(--bg-app)', 
            padding: '20px', fontSize: '15px', fontWeight: 800, borderRadius: '50px' 
          }}
        >
          {submitting ? <Loader2 size={24} className="spinner-icon" /> : 'REGISTRAR PASO AHORA'}
        </button>
      )}

      {showToast && (
        <div style={{ position: 'fixed', bottom: '32px', left: '50%', transform: 'translateX(-50%)', backgroundColor: 'var(--safe-green)', color: 'white', padding: '12px 24px', borderRadius: '50px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle size={18} /> ¡Registrado con éxito!
        </div>
      )}
      
      <style>{`
        .spinner-icon { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
