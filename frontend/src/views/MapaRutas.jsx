import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, CircleMarker, Popup } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import { MapPin, Loader2, AlertTriangle, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon issues in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Helper to fix potential encoding issues
const fixEncoding = (str) => {
  if (typeof str !== 'string') return str;
  try {
    return decodeURIComponent(escape(str));
  } catch (e) {
    return str;
  }
};

const cutPosition = [20.5666, -103.2278];

const cutIcon = new L.DivIcon({
  html: `<div style="
    background-color: var(--accent);
    color: white;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 11px;
    border: 2px solid white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  ">CUT</div>`,
  className: '',
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

export default function MapaRutas() {
  const { theme } = useTheme();
  const [rutas, setRutas] = useState([]);
  const [selectedRuta, setSelectedRuta] = useState(null);
  const [paradas, setParadas] = useState([]);
  const [incidentesMapa, setIncidentesMapa] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [proximosCamiones, setProximosCamiones] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('http://localhost:8000/api/rutas')
      .then(res => {
        const sanitized = res.data.map(r => ({
          ...r,
          nombre_ruta: fixEncoding(r.nombre_ruta),
          municipio_origen: fixEncoding(r.municipio_origen)
        }));
        setRutas(sanitized);
      })
      .catch(err => console.error("Error fetching rutas:", err));
  }, []);

  const handleRutaClick = async (ruta) => {
    if (selectedRuta?.id_ruta === ruta.id_ruta) return;
    setSelectedRuta(ruta);
    setIsLoading(true);
    setParadas([]);
    setIncidentesMapa({});

    try {
      const paradasRes = await axios.get(`http://localhost:8000/api/rutas/${ruta.id_ruta}/paradas`);
      const sanitizedParadas = paradasRes.data.map(p => ({
        ...p,
        nombre_parada: fixEncoding(p.nombre_parada)
      }));
      setParadas(sanitizedParadas);

      const incidentesRes = await axios.get('http://localhost:8000/api/incidentes/mapa');
      const incMap = {};
      if (Array.isArray(incidentesRes.data)) {
        incidentesRes.data.forEach(inc => {
          incMap[inc.id_parada] = inc.total_incidentes || 0;
        });
      }
      setIncidentesMapa(incMap);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProximoCamion = async (idParada) => {
    try {
      const res = await axios.get(`http://localhost:8000/api/paradas/${idParada}/proximos`);
      setProximosCamiones(prev => ({
        ...prev,
        [idParada]: Math.round(res.data.proximo_estimado_min) || '?'
      }));
    } catch (err) {
      setProximosCamiones(prev => ({ ...prev, [idParada]: 'N/A' }));
    }
  };

  const getMarkerColor = (count) => {
    if (!count || count === 0) return 'var(--safe-green)';
    if (count <= 2) return '#F1C40F';
    return 'var(--danger-red)';
  };

  const polylinePositions = paradas
    .map(p => [parseFloat(p.latitud), parseFloat(p.longitud)])
    .filter(pos => !isNaN(pos[0]) && !isNaN(pos[1]));

  const mapTiles = theme === 'dark' 
    ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    : "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 72px)', overflow: 'hidden' }}>
      {/* SIDEBAR */}
      <div style={{
        width: '340px',
        backgroundColor: 'var(--bg-app)',
        overflowY: 'auto',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 16px'
      }}>
        <header style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '4px' }}>Rutas Activas</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Explora el transporte al CUTonalá</p>
        </header>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {rutas.map(ruta => {
            const isSelected = selectedRuta?.id_ruta === ruta.id_ruta;
            return (
              <div
                key={ruta.id_ruta}
                onClick={() => handleRutaClick(ruta)}
                className="route-card"
                style={{
                  backgroundColor: 'var(--bg-card)',
                  border: `1px solid ${isSelected ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: '32px',
                  padding: '24px',
                  cursor: 'pointer',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  transform: isSelected ? 'translateY(-4px)' : 'none',
                  boxShadow: 'none',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <span className="text-xs-uppercase" style={{ 
                    color: isSelected ? 'var(--accent)' : 'var(--text-muted)',
                    fontWeight: 500 
                  }}>
                    {ruta.numero_camion}
                  </span>
                  <div style={{ 
                    width: '6px', height: '6px', borderRadius: '50%', 
                    backgroundColor: ruta.activa ? 'var(--safe-green)' : 'var(--danger-red)' 
                  }}></div>
                </div>
                
                <h3 style={{ 
                  fontSize: '20px', fontWeight: 900,
                  color: isSelected ? 'var(--accent)' : 'var(--text-main)',
                  marginBottom: '8px',
                  letterSpacing: '-0.04em',
                  lineHeight: 1.1
                }}>
                  {ruta.nombre_ruta}
                </h3>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '13px', color: 'var(--text-muted)', fontWeight: 300 }}>
                  <MapPin size={12} /> {ruta.municipio_origen}
                </div>

                {isSelected && (
                  <div style={{ 
                    position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                    color: 'var(--accent)'
                  }}>
                    <ChevronRight size={20} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* MAP AREA */}
      <div style={{ flex: 1, position: 'relative' }}>
        {isLoading && (
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'var(--bg-app)', opacity: 0.7,
            zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}>
            <Loader2 size={48} color="var(--accent)" className="spinner-icon" />
          </div>
        )}

        <MapContainer
          center={cutPosition}
          zoom={16}
          style={{ height: '100%', width: '100%', background: 'var(--bg-app)' }}
          zoomControl={false}
        >
          <TileLayer
            key={mapTiles} // Force reload on theme change
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url={mapTiles}
          />

          <Marker position={cutPosition} icon={cutIcon} zIndexOffset={1000} />

          {selectedRuta && paradas.length > 0 && (
            <Polyline
              key={`polyline-${selectedRuta.id_ruta}`}
              positions={polylinePositions}
              pathOptions={{ color: 'var(--accent)', weight: 4, opacity: 0.6, lineJoin: 'round' }}
            />
          )}

          {paradas.map(parada => {
            const count = incidentesMapa[parada.id_parada] || 0;
            const markerColor = getMarkerColor(count);
            const lat = parseFloat(parada.latitud);
            const lng = parseFloat(parada.longitud);

            if (isNaN(lat) || isNaN(lng)) return null;

            return (
              <CircleMarker
                key={`${selectedRuta?.id_ruta}-${parada.id_parada}`}
                center={[lat, lng]}
                radius={7}
                pathOptions={{
                  color: theme === 'dark' ? '#161B22' : 'white',
                  weight: 2,
                  fillColor: markerColor,
                  fillOpacity: 1
                }}
                eventHandlers={{
                  click: () => fetchProximoCamion(parada.id_parada)
                }}
              >
                <Popup className="custom-popup" closeButton={false}>
                  <div style={{ minWidth: '180px', color: 'var(--text-main)' }}>
                    <div style={{ fontWeight: 800, fontSize: '14px', marginBottom: '8px' }}>
                      {parada.nombre_parada}
                    </div>

                    <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                      <div style={{ 
                        backgroundColor: count > 0 ? 'rgba(231, 76, 60, 0.1)' : 'rgba(46, 204, 113, 0.1)',
                        color: count > 0 ? 'var(--danger-red)' : 'var(--safe-green)',
                        padding: '4px 8px', borderRadius: '6px', fontSize: '11px', fontWeight: 700
                      }}>
                        {count} Incidentes
                      </div>
                    </div>

                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      Próximo camión: 
                      <span style={{ fontWeight: 800, color: 'var(--accent)', marginLeft: '4px' }}>
                        {proximosCamiones[parada.id_parada] !== undefined ? `~${proximosCamiones[parada.id_parada]} min` : 'Click para calcular'}
                      </span>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>

      <style>{`
        .route-card:hover:not(.selected) {
          transform: translateX(4px);
          border-color: var(--accent) !important;
        }
        .custom-popup .leaflet-popup-content-wrapper {
          background: var(--bg-card);
          border-radius: 16px;
          border: 1px solid var(--border);
          box-shadow: var(--card-shadow);
        }
        .custom-popup .leaflet-popup-tip {
          background: var(--bg-card);
        }
        .spinner-icon { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
