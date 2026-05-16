import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react';

// ─── Shared style helpers ─────────────────────────────────────
const cardStyle = {
  background: 'var(--apple-surface)',
  borderRadius: '20px',
  padding: '40px 36px',
  width: '100%',
  maxWidth: '420px',
  boxShadow: '0 2px 20px rgba(0,0,0,0.08)',
};

const labelStyle = {
  display: 'block',
  fontSize: '13px',
  fontWeight: 500,
  color: 'var(--apple-label-2)',
  marginBottom: '6px',
};

const inputBase = {
  width: '100%',
  padding: '13px 16px',
  background: 'var(--apple-bg)',
  border: '1.5px solid transparent',
  borderRadius: '10px',
  fontSize: '15px',
  color: 'var(--apple-label)',
  fontFamily: "'DM Sans', sans-serif",
  outline: 'none',
  boxSizing: 'border-box',
  transition: 'border-color 0.2s, background 0.2s, box-shadow 0.2s',
};

// ─── Input with focus state managed via React ────────────────
function Field({ label, children }) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <label style={labelStyle}>{label}</label>
      {children}
    </div>
  );
}

function AppleInput({ focused, onFocus, onBlur, style, ...props }) {
  return (
    <input
      onFocus={onFocus}
      onBlur={onBlur}
      style={{
        ...inputBase,
        borderColor: focused ? 'var(--orange-accent)' : 'transparent',
        background: focused ? 'var(--apple-surface)' : 'var(--apple-bg)',
        boxShadow: focused ? '0 0 0 3px rgba(232,82,26,0.12)' : 'none',
        ...style,
      }}
      {...props}
    />
  );
}

// ─── Logo ─────────────────────────────────────────────────────
function Logo() {
  return (
    <div style={{ textAlign: 'center', marginBottom: '8px' }}>
      <span style={{ fontSize: '22px', fontWeight: 700, letterSpacing: '-0.5px', color: 'var(--apple-label)' }}>
        CUTG<span style={{ color: 'var(--orange-accent)' }}>O.</span>
      </span>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────
export default function Login() {
  const [nombre, setNombre]       = useState('');
  const [contrasena, setContrasena] = useState('');
  const [showPass, setShowPass]   = useState(false);
  const [error, setError]         = useState('');
  const [loading, setLoading]     = useState(false);
  const [focused, setFocused]     = useState('');

  const { login } = useAuth();
  const navigate  = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, contrasena }),
      });
      if (res.ok) {
        const userData = await res.json();
        login(userData);
        navigate('/');
      } else {
        setError('Nombre o contraseña incorrectos');
      }
    } catch {
      setError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        ::placeholder { color: rgba(60,60,67,0.4) !important; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }

        .submit-btn {
          transition: background 0.15s ease, color 0.15s ease, transform 0.1s ease, opacity 0.15s ease;
        }
        .submit-btn:hover:not([data-loading='true']) {
          background: #E5E5E5 !important;
          color: #000 !important;
        }
        .submit-btn:active:not([data-loading='true']) {
          background: var(--orange-accent) !important;
          color: #fff !important;
          transform: scale(0.98);
        }
        .submit-btn[data-loading='true'] {
          background: var(--orange-accent) !important;
          color: #fff !important;
          opacity: 0.85;
          cursor: not-allowed;
        }
      `}</style>

      <div style={{
        minHeight: '100vh',
        background: 'var(--apple-bg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px 16px',
      }}>
        <div style={cardStyle}>
          <Logo />

          <h1 style={{ fontSize: '22px', fontWeight: 700, color: 'var(--apple-label)', textAlign: 'center', marginBottom: '4px' }}>
            Bienvenido de vuelta
          </h1>
          <p style={{ fontSize: '14px', color: 'var(--apple-label-2)', textAlign: 'center', marginBottom: '28px' }}>
            Ingresa tus datos para continuar
          </p>

          <form onSubmit={handleSubmit}>
            {/* Nombre */}
            <Field label="Nombre completo">
              <AppleInput
                type="text"
                placeholder="Tu nombre completo"
                value={nombre}
                onChange={e => setNombre(e.target.value)}
                required
                focused={focused === 'nombre'}
                onFocus={() => setFocused('nombre')}
                onBlur={() => setFocused('')}
              />
            </Field>

            {/* Contraseña + toggle */}
            <Field label="Contraseña">
              <div style={{ position: 'relative' }}>
                <AppleInput
                  type={showPass ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={contrasena}
                  onChange={e => setContrasena(e.target.value)}
                  required
                  focused={focused === 'pass'}
                  onFocus={() => setFocused('pass')}
                  onBlur={() => setFocused('')}
                  style={{ paddingRight: '44px' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPass(v => !v)}
                  style={{
                    position: 'absolute',
                    right: '14px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    cursor: 'pointer',
                    color: 'var(--apple-label-2)',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              {/* Error below password */}
              {error && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: '4px',
                  color: 'var(--apple-red)', fontSize: '13px', marginTop: '6px',
                }}>
                  <AlertCircle size={14} />
                  {error}
                </div>
              )}
            </Field>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              data-loading={loading}
              className="submit-btn"
              style={{
                width: '100%',
                padding: '15px',
                background: 'var(--apple-label)',
                color: 'var(--apple-bg)',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                marginTop: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                fontFamily: "'DM Sans', sans-serif",
              }}
            >
              {loading && <Loader2 size={18} className="spin" />}
              {loading ? 'Verificando...' : 'Iniciar sesión'}
            </button>

            {/* Divider */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', margin: '20px 0' }}>
              <div style={{ flex: 1, height: '1px', background: 'var(--apple-separator)' }} />
              <span style={{ fontSize: '12px', color: 'var(--apple-label-3)', fontWeight: 500 }}>o</span>
              <div style={{ flex: 1, height: '1px', background: 'var(--apple-separator)' }} />
            </div>

            <p style={{ textAlign: 'center', fontSize: '14px', color: 'var(--apple-label-2)' }}>
              ¿Primera vez aquí?{' '}
              <Link to="/registro" style={{ color: 'var(--orange-accent)', fontWeight: 600, textDecoration: 'none' }}>
                Crear cuenta →
              </Link>
            </p>
          </form>
        </div>
      </div>
    </>
  );
}
