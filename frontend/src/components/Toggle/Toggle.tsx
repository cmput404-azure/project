import '@fortawesome/fontawesome-free/css/all.min.css';

import PeopleIcon from '@mui/icons-material/People';
import PublicIcon from '@mui/icons-material/Public';
import styles from './Toggle.module.scss';

export default function Toggle() {
    return (
      <div className={styles.toggleContainer}>
        <input type="checkbox" id="toggle" className={styles.toggleInput} />
        <label htmlFor="toggle" className={styles.toggleLabel}>
          <div className={styles.iconContainer}>
            <div className={styles.icon}>
              <PublicIcon />
            </div>
            <div className={styles.icon}>
              <PeopleIcon />
            </div>
          </div>
        </label>
      </div>
    );
  }