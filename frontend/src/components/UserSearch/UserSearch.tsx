import styles from './UserSearch.module.scss';
import '@fortawesome/fontawesome-free/css/all.min.css'
import ListItem from '../ListItem/ListItem';

export default function UserSearch(){
    return(
        <div>
            <div className = {styles.searchContainer}><i className="fa-solid fa-magnifying-glass"></i></div>
            <ListItem ></ListItem>
        </div>
    )
}