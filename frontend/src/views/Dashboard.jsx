import React, { useState, useEffect } from 'react';
import { 
  BarChart2, Users, Navigation, Clock, AlertTriangle 
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { useTheme } from '../context/ThemeContext';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const MetricCard = ({ title, value, icon: Icon, color, loading }) => (
  <div style={{
    backgroundColor: 'var(--bg-card)',
    borderRadius: '16px',
    padding: '24px',
    borderTop: `4px solid ${color}`,
    boxShadow: 'var(--card-shadow)',
    display: 'flex',
    flexDirection: 'column',
    transition: 'transform 0.3s ease'
  }}>
    <Icon size={24} color={color} />
    {loading ? (
      <div className="skeleton-bar" style={{ width: '80px', height: '32px', marginTop: '12px', borderRadius: '4px' }}></div>
    ) : (
      <div style={{ fontSize: '36px', fontWeight: 900, color: 'var(--text-main)', marginTop: '12px', letterSpacing: '-0.03em' }}>
        {value}
      </div>
    )}
    <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '6px', fontWeight: 500, letterSpacing: '0.05em' }}>{title}</div>
  </div>
);

const ChartCard = ({ title, children }) => (
  <div style={{
    backgroundColor: 'var(--bg-card)',
    borderRadius: '16px',
    padding: '24px',
    boxShadow: 'var(--card-shadow)',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    border: '1px solid var(--border)'
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
      <h3 style={{ fontSize: '15px', fontWeight: 900, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>{title}</h3>
      <div style={{ 
        backgroundColor: 'var(--bg-app)', 
        color: 'var(--text-muted)', 
        fontSize: '11px', 
        padding: '4px 10px', 
        borderRadius: '6px',
        fontWeight: 600,
        letterSpacing: '0.05em'
      }}>
        LATEST 30 DAYS
      </div>
    </div>
    <div style={{ flex: 1, position: 'relative', minHeight: '280px' }}>
      {children}
    </div>
  </div>
);

export default function Dashboard() {
  const { theme } = useTheme();
  const [resumen, setResumen] = useState(null);
  const [incidentesRuta, setIncidentesRuta] = useState([]);
  const [frecuencia, setFrecuencia] = useState([]);
  const [calificaciones, setCalificaciones] = useState([]);
  const [loading, setLoading] = useState(true);

  // Dynamic Chart Colors
  const textColor = theme === 'dark' ? '#F3F4F6' : '#111827';
  const mutedColor = theme === 'dark' ? '#9CA3AF' : '#6B7280';
  const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.05)';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resRes, incRes, freRes, calRes] = await Promise.all([
          fetch('http://localhost:8000/api/estadisticas/resumen'),
          fetch('http://localhost:8000/api/estadisticas/incidentes-por-ruta'),
          fetch('http://localhost:8000/api/estadisticas/frecuencia'),
          fetch('http://localhost:8000/api/estadisticas/calificaciones')
        ]);

        if (resRes.ok) setResumen(await resRes.json());
        if (incRes.ok) setIncidentesRuta(await incRes.json());
        if (freRes.ok) setFrecuencia(await freRes.json());
        if (calRes.ok) setCalificaciones(await calRes.json());
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
        labels: { color: textColor, font: { weight: 600 } }
      },
      tooltip: {
        backgroundColor: theme === 'dark' ? '#161B22' : '#FFFFFF',
        titleColor: textColor,
        bodyColor: textColor,
        borderColor: gridColor,
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        grid: { color: gridColor, drawBorder: false },
        ticks: { color: mutedColor, font: { size: 11 } }
      },
      y: {
        grid: { color: gridColor, drawBorder: false },
        ticks: { color: mutedColor, font: { size: 11 } }
      }
    }
  };

  const incidentesChartData = {
    labels: incidentesRuta.map(r => r.nombre_ruta),
    datasets: [{
      data: incidentesRuta.map(r => r.total),
      backgroundColor: theme === 'dark' ? 'rgba(255, 122, 48, 0.8)' : 'rgba(231, 76, 60, 0.8)',
      borderRadius: 6,
      barThickness: 20
    }]
  };

  const sortedFrecuencia = [...frecuencia].sort((a, b) => a.frecuencia_min - b.frecuencia_min).slice(0, 7);
  const frecuenciaChartData = {
    labels: sortedFrecuencia.map(p => p.nombre_parada),
    datasets: [{
      label: 'Frecuencia (min)',
      data: sortedFrecuencia.map(p => p.frecuencia_min),
      backgroundColor: 'rgba(0, 48, 135, 0.75)',
      borderRadius: 6,
      barThickness: 20
    }]
  };

  const calificacionesChartData = {
    labels: calificaciones.map(c => c.nombre_ruta),
    datasets: [{
      data: calificaciones.map(c => c.promedio_seguridad),
      backgroundColor: calificaciones.map(c => {
        const val = c.promedio_seguridad;
        if (val >= 4.0) return '#2ECC71';
        if (val >= 3.0) return '#F1C40F';
        return '#E74C3C';
      }),
      borderRadius: 6,
      barThickness: 24
    }]
  };

  return (
    <div style={{ backgroundColor: 'var(--bg-app)', minHeight: 'calc(100vh - 72px)', padding: '40px 24px' }}>
      <header style={{ marginBottom: '48px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          <h1 style={{ fontSize: '36px', fontWeight: 900, letterSpacing: '-0.03em' }}>Panel de Estadísticas</h1>
          <BarChart2 size={32} color="var(--accent)" />
        </div>
        <p className="text-xs-uppercase" style={{ color: 'var(--text-muted)' }}>
          {new Date().toLocaleDateString('es-MX', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </header>

      {/* ROW 1: Metric Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
        gap: '24px',
        marginBottom: '40px'
      }}>
        <MetricCard 
          title="USUARIOS REGISTRADOS" 
          value={resumen?.total_usuarios} 
          icon={Users} 
          color="var(--accent)" 
          loading={loading} 
        />
        <MetricCard 
          title="RUTAS ACTIVAS" 
          value={resumen?.total_rutas_activas} 
          icon={Navigation} 
          color="#8B5CF6" 
          loading={loading} 
        />
        <MetricCard 
          title="HORARIOS REGISTRADOS" 
          value={resumen?.total_registros_horario} 
          icon={Clock} 
          color="var(--safe-green)" 
          loading={loading} 
        />
        <MetricCard 
          title="INCIDENTES ESTE MES" 
          value={resumen?.incidentes_este_mes} 
          icon={AlertTriangle} 
          color="var(--danger-red)" 
          loading={loading} 
        />
      </div>

      {/* ROW 2: Two charts side by side */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', 
        gap: '24px',
        marginBottom: '40px'
      }}>
        <ChartCard title="Incidentes por Ruta">
          <Bar 
            data={incidentesChartData} 
            options={{
              ...commonOptions,
              indexAxis: 'y',
              scales: {
                ...commonOptions.scales,
                x: { ...commonOptions.scales.x, beginAtZero: true },
                y: { ...commonOptions.scales.y, grid: { display: false } }
              }
            }} 
          />
        </ChartCard>

        <ChartCard title="Frecuencia por Parada">
          <Bar 
            data={frecuenciaChartData} 
            options={{
              ...commonOptions,
              indexAxis: 'y',
              scales: {
                ...commonOptions.scales,
                x: { ...commonOptions.scales.x, beginAtZero: true },
                y: { ...commonOptions.scales.y, grid: { display: false } }
              }
            }} 
          />
        </ChartCard>
      </div>

      {/* ROW 3: Safety rating chart (full width) */}
      <div style={{ marginBottom: '40px' }}>
        <ChartCard title="Calificación de Seguridad">
          <Bar 
            data={calificacionesChartData} 
            options={{
              ...commonOptions,
              scales: {
                ...commonOptions.scales,
                y: { ...commonOptions.scales.y, min: 0, max: 5, ticks: { ...commonOptions.scales.y.ticks, stepSize: 1 } },
                x: { ...commonOptions.scales.x, grid: { display: false } }
              }
            }} 
          />
        </ChartCard>
      </div>

      <style>{`
        .skeleton-bar {
          background: var(--border);
          opacity: 0.1;
          animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
          0% { opacity: 0.1; }
          50% { opacity: 0.3; }
          100% { opacity: 0.1; }
        }
      `}</style>
    </div>
  );
}
