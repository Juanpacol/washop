import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from './Sidebar.module.css';

const NAV_GROUPS = [
  {
    label: 'MAIN',
    items: [
      { to: '/', label: 'Dashboard', end: true },
      { to: '/services', label: 'Services', badge: true },
    ],
  },
  {
    label: 'MANAGEMENT',
    items: [
      { to: '/customers', label: 'Customers' },
      { to: '/payments', label: 'Payments' },
      { to: '/reports', label: 'Reports' },
    ],
  },
  {
    label: 'SYSTEM',
    items: [
      { to: '/settings', label: 'Settings' },
    ],
  },
];

export default function Sidebar({ servicesBadge = 0 }) {
  const { signOut } = useAuth();

  return (
    <nav className={styles.sidebar}>
      <div className={styles.logo}>WASHOPS</div>

      <div className={styles.nav}>
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className={styles.group}>
            <div className={styles.groupLabel}>{group.label}</div>
            {group.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `${styles.navItem}${isActive ? ` ${styles.active}` : ''}`
                }
              >
                {item.label}
                {item.badge && servicesBadge > 0 && (
                  <span className={styles.badge}>{servicesBadge}</span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </div>

      <div className={styles.footer}>
        <button className={styles.logoutBtn} onClick={signOut}>
          Cerrar sesión
        </button>
      </div>
    </nav>
  );
}
