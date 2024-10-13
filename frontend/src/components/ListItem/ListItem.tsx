import styles from './ListItem.module.scss';

interface ListItemProps {
    isRequest: boolean;
    isPost: boolean;
    isLike: boolean;
    isFollowerList: boolean;
}

export default function ListItem({
    isRequest,
    isPost,
    isLike,
    isFollowerList,
}: ListItemProps) {
    let additionalText = "";

    if (isFollowerList) {
        additionalText = "accepted your follow request";
    } else if (isRequest) {
        additionalText = "wants to follow you";
    }
    else if (isLike) {
        additionalText = "liked your post";
    } else if (isPost) {
        additionalText = "shared a post with you";
    }
    return (
        <div className={styles.ListItemContainer}>
            <div className={styles.container}>
                <img className={styles.listImg} src='../images/Shiba-pfp.jpg' alt='pfp' />
                <div className={styles.text}>
                    <h1>Garfield
                    <span className={styles.additionalText}>{additionalText}</span>
                    </h1>
                    <p>@Garfield890</p>
                </div>

                {isFollowerList ? <button>Unfollow</button> : null}
                {isRequest ? <span><button>Accept</button> <button>Decline</button></span> : null}
                {isPost ? <img className={styles.listImgPost} src='../images/Shiba-pfp.jpg' alt='pfp' /> : null}
            </div>
        </div>
    )
}