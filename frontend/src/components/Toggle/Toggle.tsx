import styles from './Toggle.module.scss';
import '@fortawesome/fontawesome-free/css/all.min.css';

export default function Toggle() {
    return (
      <div className={styles.toggleContainer}>
        <input type="checkbox" id="toggle" className={styles.toggleInput} />
        <label htmlFor="toggle" className={styles.toggleLabel}>
          <div className={styles.iconContainer}>
            <div className={`${styles.icon} ${styles.globe}`}><i className="fa-solid fa-earth-americas"></i></div>
            <div className={`${styles.icon} ${styles.users}`}><i className="fa-solid fa-user-group"></i></div>
          </div>
        </label>
      </div>
    );
  }