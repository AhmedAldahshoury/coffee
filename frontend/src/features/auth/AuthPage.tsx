import { FormEvent, useState } from 'react';
import { login, register } from './authApi';
import { useNavigate } from 'react-router-dom';

export function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = mode === 'login' ? await login({ email, password }) : await register({ email, password });
      localStorage.setItem('coffee_token', res.access_token);
      navigate('/optimizer');
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel auth-panel">
      <h2>{mode === 'login' ? 'Login' : 'Register'}</h2>
      <form onSubmit={onSubmit} className="form-grid">
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button className="btn" disabled={loading}>{loading ? 'Please wait...' : mode}</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}
