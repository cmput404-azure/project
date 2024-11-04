import { Comment } from "@mui/icons-material";
import Modal from "react-modal";
import React, { useEffect, useState } from "react";
import styles from "./CommentView.module.scss";
import CommentInputField from "../CommentInput/CommentInput";

interface Comment {
  id: number;
  author: {
    id: string;
    type: string;
    displayName: string;
    profileImage?: string;
  };
  comment: string;
  contentType: string;
  published: string;
}

interface CommentViewProps {
  isOpen: boolean;
  onRequestClose: () => void;
  postComponent: React.ReactNode;
  comments: Comment[]; // List of comments
  author: any; // author object
  post: any;
}

const CommentView: React.FC<CommentViewProps> = ({
  isOpen,
  onRequestClose,
  postComponent,
  comments,
  author,
  post
}) => {
  console.log("Comments", comments);

  const [commentList, setCommentList] = useState([...comments])

  const handleNewComment = (newComment) => {
    const newCommentList = [...commentList, newComment]
    setCommentList(newCommentList)
  }

    // Use useEffect to update commentList when comments prop changes
    useEffect(() => {
      setCommentList([...comments]);
    }, [comments]);
  


  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      className={styles.modalContent}
      overlayClassName={styles.modalOverlay}
    >
      {/* Post Component */}
      <div className={styles.post}>{postComponent}</div>

      <section className={styles.comments}>
        <div className={styles.commentsHeader}>Comments</div>

        {/* Comments Section */}
        <div className={styles.commentsSection}>
          {/* Comment Input Field */}
          {!(author == null) && <CommentInputField authorObj={author} post={post}  onCommentAdded={handleNewComment}/>}

          {commentList.map((comment) => (
            <div key={comment.id} className={styles.comment}>
              <div key={comment.id} className={styles.comment}>
                <img
                  src={
                    author.profileImage
                      ? author.profileImage
                      : `https://ui-avatars.com/api/?background=random&name=${comment.author.displayName}`
                  }
                  className={styles.userImage}
                />
              </div>
              <div className={styles.commentContent}>
                <div className={styles.authorTime}>
                  <div className={styles.commentAuthor}>
                    {comment.author.displayName}
                  </div>
                  <div className={styles.timePosted}>{new Date(comment.published).toLocaleString()}</div>
                </div>
                <div className={styles.commentText}>{comment.comment}</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </Modal>
  );
};

export default CommentView;
