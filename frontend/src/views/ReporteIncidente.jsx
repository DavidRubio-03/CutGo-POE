import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, AlertTriangle, UserX, Car, Users, Clock, 
  MoreHorizontal, X, ShieldCheck, MapPin, Loader2 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link, Navigate } from 'react-router-dom';

const INCIDENT_TYPES = [
  { id: 'robo', label: 'Robo / Asalto', icon: AlertTriangle, color: 'var(--danger-red)', bg: 'rgba(231, 76, 60, 0.1)' },
  { id: 'acoso', label: 'Acoso', icon: UserX, color: 'var(--accent)', bg: 'rgba(255, 92, 0, 0.1)' },
  { id: 'accidente', label: 'Accidente', icon: Car, color: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.1)' },
  { id: 'camion_lleno', label: 'Camión lleno', icon: Users, color: '#6B7280', bg: 'rgba(107, 114, 128, 0.1)' },
  { id: 'retraso', label: 'Retraso', icon: Clock, color: '#F1C40F', bg: 'rgba(241, 196, 15, 0.1)' },
  { id: 'otro', label: 'Otro', icon: MoreHorizontal, color: '#6B7280', bg: 'rgba(107, 114, 128, 0.1)' },
];

export default function ReporteIncidente() {
  const { user } = useAuth();
  const [allStops, setAllStops] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredStops, setFilteredStops] = useState([]);
  const [selectedStop, setSelectedStop] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [description, setDescription] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [isLoadingStops, setIsLoadingStops] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const rutasRes = await fetch('http://localhost:8000/api/rutas');
        const rutas = await rutasRes.json();
        const stopsPromises = rutas.map(async (ruta) => {
          const stopsRes = await fetch(`http://localhost:8000/api/rutas/${ruta.id_ruta}/paradas`);
          const stops = await stopsRes.json();
          return stops.map(s => ({ ...s, nombre_ruta: ruta.nombre_ruta }));
        });
        const results = await Promise.all(stopsPromises);
        setAllStops(results.flat());
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoadingStops(false);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    if (searchTerm.trim().length > 1) {
      const filtered = allStops.filter(stop => 
        stop.nombre_parada.toLowerCase().includes(searchTerm.toLowerCase())
      ).slice(0, 5);
      setFilteredStops(filtered);
    } else {
      setFilteredStops([]);
    }
  }, [searchTerm, allStops]);

  const handleFinalSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch('http://localhost:8000/api/incidentes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_parada: selectedStop.id_parada,
          id_usuario: user.id_usuario,
          tipo_incidente: selectedType.id,
          description: description
        })
      });
      if (response.ok) setSuccess(true);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) return <Navigate to="/login" />;

  if (success) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '100px 24px', textAlign: 'center' }}>
        <ShieldCheck size={80} color="var(--safe-green)" style={{ marginBottom: '24px' }} />
        <h2 style={{ fontSize: '32px', marginBottom: '16px' }}>Reporte Enviado</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '40px' }}>Tu contribución ayuda a mantener seguras nuestras rutas.</p>
        <button onClick={() => setSuccess(false)} style={{ backgroundColor: 'var(--text-main)', color: 'var(--bg-app)', padding: '14px 32px', borderRadius: '50px' }}>
          Volver a reportar
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '40px 24px', maxWidth: '600px', margin: '0 auto' }}>
      <header style={{ marginBottom: '48px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '36px', fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1.1 }}>Reportar Incidente</h2>
          <ShieldAlert size={32} color="var(--accent)" />
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '15px', fontWeight: 300 }}>Tu reporte anónimo ayuda a mantener seguras las rutas.</p>
      </header>

      <div className="glass-card" style={{ padding: '32px', marginBottom: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <label className="text-xs-uppercase" style={{ display: 'block', marginBottom: '10px' }}>¿En qué parada ocurrió?</label>
          {!selectedStop ? (
            <div style={{ position: 'relative' }}>
              <input 
                type="text" 
                placeholder="Buscar parada..." 
                value={searchTerm} 
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ width: '100%', padding: '16px', borderRadius: '16px', border: '1px solid var(--border)', background: 'var(--bg-app)', color: 'var(--text-main)', fontSize: '14px' }}
              />
              {filteredStops.length > 0 && (
                <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '16px', marginTop: '8px', zIndex: 10, overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.1)' }}>
                  {filteredStops.map(stop => (
                    <div 
                      key={stop.id_parada} 
                      onClick={() => { setSelectedStop(stop); setSearchTerm(''); setFilteredStops([]); }}
                      style={{ padding: '14px 16px', cursor: 'pointer', borderBottom: '1px solid var(--border)', transition: 'background 0.2s' }}
                      onMouseOver={(e) => e.currentTarget.style.background = 'rgba(0,0,0,0.02)'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div style={{ fontSize: '14px', fontWeight: 700 }}>{stop.nombre_parada}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 300 }}>{stop.nombre_ruta}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 20px', background: 'rgba(255, 92, 0, 0.05)', borderRadius: '50px', border: '1px solid var(--accent)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MapPin size={16} color="var(--accent)" />
                <span style={{ fontSize: '14px', fontWeight: 700 }}>{selectedStop.nombre_parada}</span>
              </div>
              <X size={18} style={{ cursor: 'pointer', color: 'var(--text-muted)' }} onClick={() => setSelectedStop(null)} />
            </div>
          )}
        </div>

        <div style={{ marginBottom: '32px' }}>
          <label className="text-xs-uppercase" style={{ display: 'block', marginBottom: '16px' }}>Tipo de incidente</label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {INCIDENT_TYPES.map(type => {
              const Icon = type.icon;
              const isSelected = selectedType?.id === type.id;
              return (
                <button 
                  key={type.id} 
                  onClick={() => setSelectedType(type)}
                  style={{ 
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', padding: '20px 8px', borderRadius: '24px', 
                    border: '1px solid', borderColor: isSelected ? type.color : 'var(--border)',
                    background: isSelected ? type.bg : 'transparent', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                  }}
                >
                  <Icon size={24} color={isSelected ? type.color : 'var(--text-muted)'} />
                  <span style={{ fontSize: '11px', fontWeight: isSelected ? 800 : 400, color: isSelected ? 'var(--text-main)' : 'var(--text-muted)' }}>{type.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <button 
          disabled={!selectedStop || !selectedType || isSubmitting}
          onClick={handleFinalSubmit}
          style={{ 
            width: '100%', backgroundColor: 'var(--text-main)', color: 'var(--bg-app)', 
            padding: '18px', fontSize: '15px', fontWeight: 800, borderRadius: '50px' 
          }}
        >
          {isSubmitting ? <Loader2 size={20} className="spinner-icon" /> : 'CONFIRMAR REPORTE'}
        </button>
      </div>
      
      <style>{`
        .spinner-icon { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
