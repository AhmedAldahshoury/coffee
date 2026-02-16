import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogoMark, SparkIcon } from '../../components/icons';
import { login, register } from './authApi';

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
    <section className="auth-layout fade-in-up">
      <aside className="panel auth-hero">
        <LogoMark size={44} />
        <p className="eyebrow">Coffee Optimizer</p>
        <h2>Turn every brew into a repeatable result.</h2>
        <p className="muted">A premium workspace for calibrated experiments, clear metrics, and better coffee.</p>
        <ul className="token-list">
          <li><SparkIcon size={14} /> Precision trial tracking</li>
          <li><SparkIcon size={14} /> Live feedback and score trends</li>
          <li><SparkIcon size={14} /> Leaderboard-backed calibration</li>
        </ul>
      </aside>

      <div className="panel auth-panel">
        <p className="eyebrow">{mode === 'login' ? 'Welcome back' : 'Create account'}</p>
        <h2>{mode === 'login' ? 'Sign in to continue' : 'Get started in seconds'}</h2>
        <p className="muted">Use your email and password to access your optimizer workspace.</p>

        <form onSubmit={onSubmit} className="form-grid">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </label>
          <button className="btn btn-primary" disabled={loading}>{loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Register'}</button>
        </form>

        {error ? <p className="error">{error}</p> : null}

        <p className="muted auth-switch">
          {mode === 'login' ? 'Need an account?' : 'Already have an account?'}{' '}
          <Link to={mode === 'login' ? '/register' : '/login'}>
            {mode === 'login' ? 'Register' : 'Login'}
          </Link>
        </p>
      </div>
    </section>
  );
}
