import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, Loader2, CheckCircle, X, CheckCircle2 } from 'lucide-react';

// ─── Shared styles ────────────────────────────────────────────
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
  appearance: 'none',
};

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

function AppleSelect({ focused, onFocus, onBlur, children, ...props }) {
  return (
    <select
      onFocus={onFocus}
      onBlur={onBlur}
      style={{
        ...inputBase,
        borderColor: focused ? 'var(--orange-accent)' : 'transparent',
        background: focused ? 'var(--apple-surface)' : 'var(--apple-bg)',
        boxShadow: focused ? '0 0 0 3px rgba(232,82,26,0.12)' : 'none',
        cursor: 'pointer',
      }}
      {...props}
    >
      {children}
    </select>
  );
}

function Logo() {
  return (
    <div style={{ textAlign: 'center', marginBottom: '8px' }}>
      <span style={{ fontSize: '22px', fontWeight: 700, letterSpacing: '-0.5px', color: 'var(--apple-label)' }}>
        CUTG<span style={{ color: 'var(--orange-accent)' }}>O.</span>
      </span>
    </div>
  );
}

// ─── Success state ────────────────────────────────────────────
function SuccessState() {
  return (
    <div style={{ textAlign: 'center', padding: '16px 0' }}>
      <CheckCircle2 size={48} color="var(--apple-green)" strokeWidth={1.5} style={{ marginBottom: '16px' }} />
      <h2 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--apple-label)', marginBottom: '8px' }}>
        ¡Listo!
      </h2>
      <p style={{ fontSize: '14px', color: 'var(--apple-label-2)' }}>
        Tu cuenta fue creada exitosamente
      </p>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────
export default function Registro() {
  const [formData, setFormData] = useState({
    nombre: '',
    carrera: '',
    semestre: '1',
    municipio_origen: '',
    contrasena: '',
    confirmarContrasena: '',
  });
  const [showPass,    setShowPass]    = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [success,  setSuccess]  = useState(false);
  const [focused,  setFocused]  = useState('');

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
  };

  const passwordsMatch =
    formData.confirmarContrasena.length > 0 &&
    formData.contrasena === formData.confirmarContrasena;

  const passwordsMismatch =
    formData.confirmarContrasena.length > 0 &&
    formData.contrasena !== formData.confirmarContrasena;

  const canSubmit =
    !loading &&
    formData.nombre.trim() !== '' &&
    formData.carrera !== '' &&
    formData.municipio_origen.trim() !== '' &&
    formData.contrasena !== '' &&
    formData.contrasena === formData.confirmarContrasena;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.contrasena.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    if (!passwordsMatch) {
      setError('Las contraseñas no coinciden');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: formData.nombre,
          carrera: formData.carrera,
          semestre: parseInt(formData.semestre),
          municipio_origen: formData.municipio_origen,
          contrasena: formData.contrasena,
        }),
      });

      if (res.ok) {
        setSuccess(true);
        setTimeout(() => navigate('/login'), 2000);
      } else {
        const data = await res.json();
        setError(data.detail || 'Error al registrar usuario');
      }
    } catch {
      setError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  const f = (name) => ({
    focused: focused === name,
    onFocus: () => setFocused(name),
    onBlur: () => setFocused(''),
  });

  return (
    <>
      <style>{`
        ::placeholder { color: rgba(60,60,67,0.4) !important; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
        select option { background: var(--apple-surface); color: var(--apple-label); }

        .submit-btn {
          transition: background 0.15s ease, color 0.15s ease, transform 0.1s ease, opacity 0.15s ease;
        }
        .submit-btn:hover:not(:disabled):not([data-loading='true']) {
          background: #E5E5E5 !important;
          color: #000 !important;
        }
        .submit-btn:active:not(:disabled):not([data-loading='true']) {
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

          {success ? (
            <SuccessState />
          ) : (
            <>
              <h1 style={{ fontSize: '22px', fontWeight: 700, color: 'var(--apple-label)', textAlign: 'center', marginBottom: '4px' }}>
                Crear cuenta
              </h1>
              <p style={{ fontSize: '14px', color: 'var(--apple-label-2)', textAlign: 'center', marginBottom: '28px' }}>
                Solo para estudiantes del CUT
              </p>

              <form onSubmit={handleSubmit}>

                {/* Nombre */}
                <Field label="Nombre completo">
                  <AppleInput
                    type="text"
                    name="nombre"
                    placeholder="Tu nombre completo"
                    value={formData.nombre}
                    onChange={handleChange}
                    required
                    {...f('nombre')}
                  />
                </Field>

                {/* Carrera */}
                <Field label="Carrera">
                  <AppleSelect name="carrera" value={formData.carrera} onChange={handleChange} required {...f('carrera')}>
                    <option value="">Selecciona una carrera...</option>
                    <option value="Ing. en Ciencias Computacionales">Ing. en Ciencias Computacionales</option>
                    <option value="Ing. en Diseño Industrial">Ing. en Diseño Industrial</option>
                    <option value="Ing. en Nanotecnología">Ing. en Nanotecnología</option>
                    <option value="Medicina">Medicina</option>
                    <option value="Enfermería y Obstetricia">Enfermería y Obstetricia</option>
                    <option value="Nutrición">Nutrición</option>
                    <option value="Otra carrera">Otra carrera</option>
                  </AppleSelect>
                </Field>

                {/* Semestre + Municipio side by side */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div>
                    <label style={labelStyle}>Semestre</label>
                    <AppleSelect name="semestre" value={formData.semestre} onChange={handleChange} {...f('semestre')}>
                      {[...Array(10)].map((_, i) => (
                        <option key={i + 1} value={i + 1}>{i + 1}</option>
                      ))}
                    </AppleSelect>
                  </div>
                  <div>
                    <label style={labelStyle}>Municipio de origen</label>
                    <AppleInput
                      type="text"
                      name="municipio_origen"
                      placeholder="Ej: Zapopan"
                      value={formData.municipio_origen}
                      onChange={handleChange}
                      required
                      {...f('municipio')}
                    />
                  </div>
                </div>

                {/* Contraseña */}
                <Field label="Contraseña">
                  <div style={{ position: 'relative' }}>
                    <AppleInput
                      type={showPass ? 'text' : 'password'}
                      name="contrasena"
                      placeholder="Mínimo 6 caracteres"
                      value={formData.contrasena}
                      onChange={handleChange}
                      required
                      {...f('pass')}
                      style={{ paddingRight: '44px' }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPass(v => !v)}
                      style={{ position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', padding: 0, cursor: 'pointer', color: 'var(--apple-label-2)', display: 'flex', alignItems: 'center' }}
                    >
                      {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </Field>

                {/* Confirmar contraseña */}
                <Field label="Confirmar contraseña">
                  <div style={{ position: 'relative' }}>
                    <AppleInput
                      type={showConfirm ? 'text' : 'password'}
                      name="confirmarContrasena"
                      placeholder="Repite tu contraseña"
                      value={formData.confirmarContrasena}
                      onChange={handleChange}
                      required
                      {...f('confirm')}
                      style={{ paddingRight: '72px' }}
                    />
                    {/* Match indicator icon */}
                    {formData.confirmarContrasena.length > 0 && (
                      <span style={{ position: 'absolute', right: '40px', top: '50%', transform: 'translateY(-50%)', display: 'flex', alignItems: 'center' }}>
                        {passwordsMatch
                          ? <CheckCircle size={16} color="var(--apple-green)" />
                          : <X size={16} color="var(--apple-red)" />
                        }
                      </span>
                    )}
                    {/* Show/hide toggle */}
                    <button
                      type="button"
                      onClick={() => setShowConfirm(v => !v)}
                      style={{ position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', padding: 0, cursor: 'pointer', color: 'var(--apple-label-2)', display: 'flex', alignItems: 'center' }}
                    >
                      {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </Field>

                {/* Error message */}
                {error && (
                  <p style={{ fontSize: '13px', color: 'var(--apple-red)', marginBottom: '8px', marginTop: '-4px' }}>
                    {error}
                  </p>
                )}

                {/* Submit */}
                <button
                  type="submit"
                  disabled={!canSubmit}
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
                    cursor: canSubmit ? 'pointer' : 'not-allowed',
                    marginTop: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    opacity: canSubmit ? 1 : 0.4,
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                >
                  {loading && <Loader2 size={18} className="spin" />}
                  {loading ? 'Creando cuenta...' : 'Crear cuenta'}
                </button>

                <p style={{ textAlign: 'center', fontSize: '14px', color: 'var(--apple-label-2)', marginTop: '20px' }}>
                  ¿Ya tienes cuenta?{' '}
                  <Link to="/login" style={{ color: 'var(--orange-accent)', fontWeight: 600, textDecoration: 'none' }}>
                    Iniciar sesión →
                  </Link>
                </p>
              </form>
            </>
          )}
        </div>
      </div>
    </>
  );
}
