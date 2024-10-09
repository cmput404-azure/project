import styles from './ListItem.module.scss';

export default function ListItem(){
    return(
        <div className={styles.ListItemContainer}>
        <div className = {styles.container}>
            <img className = {styles.listImg} src='../images/Shiba-pfp.jpg' alt='pfp'/>
            <div className = {styles.text}>
            <h1>Garfield</h1>
            <p>@Garfield890</p>
            </div>
            <button>Unfollow</button>
        </div>
        </div>
    )
}