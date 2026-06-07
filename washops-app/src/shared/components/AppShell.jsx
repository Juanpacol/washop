import Sidebar from './Sidebar';
import styles from './AppShell.module.css';

export default function AppShell({ children }) {
  return (
    <div className={styles.shell}>
      <div className={styles.sidebar}>
        <Sidebar />
      </div>
      <main className={styles.content}>
        {children}
      </main>
    </div>
  );
}
