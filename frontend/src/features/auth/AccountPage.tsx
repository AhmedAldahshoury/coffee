import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckIcon, SparkIcon } from '../../components/icons';
import { useThemeStore } from '../../shared/config/themeStore';

export function AccountPage() {
  const navigate = useNavigate();
  const { darkMode } = useThemeStore();
  const token = localStorage.getItem('coffee_token');

  const tokenPreview = useMemo(() => {
    if (!token) return 'No active token';
    return `${token.slice(0, 10)}…${token.slice(-8)}`;
  }, [token]);

  return (
    <section className="panel fade-in-up">
      <p className="eyebrow">Account</p>
      <h2>Preferences & session</h2>
      <p className="muted">Manage your session and app appearance from one place.</p>

      <div className="settings-grid">
        <article className="panel subpanel">
          <div className="row-title">
            <SparkIcon size={16} />
            <h3>Theme profile</h3>
          </div>
          <p className="muted">Current mode: {darkMode ? 'Premium Dark Espresso' : 'Light Roast'}.</p>
          <ul className="token-list">
            <li><CheckIcon size={14} /> High-contrast typography</li>
            <li><CheckIcon size={14} /> Caramel accent actions</li>
            <li><CheckIcon size={14} /> Subtle depth and motion</li>
          </ul>
        </article>

        <article className="panel subpanel">
          <div className="row-title">
            <SparkIcon size={16} />
            <h3>Session details</h3>
          </div>
          <p className="muted">Token preview</p>
          <pre className="result-box">{tokenPreview}</pre>
          <button
            className="btn btn-secondary"
            type="button"
            onClick={() => {
              localStorage.removeItem('coffee_token');
              navigate('/login');
            }}
          >
            End session
          </button>
        </article>
      </div>
    </section>
  );
}
