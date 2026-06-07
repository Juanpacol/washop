import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signIn } from '../../lib/db';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await signIn(email, password);
      navigate('/');
    } catch {
      setError('Credenciales incorrectas');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>WASHOPS</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <label className={styles.label}>
            Email
            <input
              type="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label className={styles.label}>
            Contraseña
            <input
              type="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" className={styles.button} disabled={loading}>
            {loading ? 'Iniciando...' : 'Iniciar sesión'}
          </button>
        </form>
      </div>
    </div>
  );
}
