import styles from './UserSearch.module.scss';
import '@fortawesome/fontawesome-free/css/all.min.css'
import ListItem from '../ListItem/ListItem';

export default function UserSearch() {
    return (
        <div className={styles.componentWidth}>
            <div className={styles.searchContainer}>
                <i className="fa-solid fa-magnifying-glass"></i>
                <input className={styles.searchInput} type="text" placeholder="Search..." />
                </div>
            {/* <ListItem isRequest={false} isPost={false} isLike={false} isFollowerList={false} displayName='B'></ListItem> */}
        </div>
    )
}