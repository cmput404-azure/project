import "@fortawesome/fontawesome-free/css/all.min.css";

import { useEffect, useState } from "react";

import { ContentType } from "../../models/modelTypes";
import DeletePostModal from "../DeletePostModal/DeletePostModal";
import EditPostModal from "../EditPostModal/EditPostModal";
import { PostData } from "../../models/models";
import ReactMarkdown from 'react-markdown';
import { api } from "../../service/config";
import { extractUUID } from "../../util/formatting/extractUUID";
import follow from "../../service/follow";
import { formatCount } from "../../util/formatting/formatCount";
import inbox from "../../service/inbox";
import { normalizeVisibility } from "../../util/formatting/normalizeVisibility";
import profileService from "../../service/profile";
import remarkGfm from 'remark-gfm';
import styles from "./MiniPostCard.module.scss";

interface MiniPostCardProps {
  post: PostData;
  authorUUID: string;
  onDelete?: (postId: string) => void;
}

function MiniPostCard({ post, authorUUID, onDelete }: MiniPostCardProps) {
  const [editModal, setEditModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [postData, setPostData] = useState<PostData>(post);  // Initialize state with post prop

  const openEditModal = () => setEditModal(true);
  const closeEditModal = () => setEditModal(false);
  const openDeleteModal = () => setDeleteModal(true);
  const closeDeleteModal = () => setDeleteModal(false);

  useEffect(() => {
    const fetchImage = async () => {
      if (postData.contentType === ContentType.MARKDOWN) {
        const imageRegex = /!\[.*?\]\((.*?)\)/;
        const match = postData.content.match(imageRegex);
        if (match) {
          const imageUrl = match[1];
          if (imageUrl.startsWith("data:")) {
            setImageSrc(imageUrl);
          } else {
            try {
              const response = await fetch(imageUrl);
              if (response.ok) {
                const jsonResponse = await response.json();
                const imageData = jsonResponse.image;
                setImageSrc(imageData);
              } else {
                console.error("Error fetching image:", response.statusText);
              }
            } catch (error) {
              console.error("Error fetching image:", error);
            }
          }
        }
      }
    };

    fetchImage();
  }, [postData.content, postData.contentType]);

  async function handleUpdatePost(updatedPost: {
    title: string;
    content: string;
    visibility: number;
  }) {
    try {
      const postId = extractUUID(postData.id);
      await api.put(`/api/authors/${extractUUID(authorUUID)}/posts/${postId}/`, updatedPost);

      const followers = await follow.getFollowers(extractUUID(authorUUID));
      const friends = await follow.getFriends(extractUUID(authorUUID));
      const target = normalizeVisibility(updatedPost.visibility) === 1 || normalizeVisibility(updatedPost.visibility) === 3 ? followers : friends;
      for (const recipient of target) {
        const post_obj = {
          ...postData,
          ...(postData.type ? {} : { type: "post" }),
          title: updatedPost.title,
          content: updatedPost.content,
          visibility: normalizeVisibility(updatedPost.visibility, true) as string,
          follower: {
            type: "author",
            id: recipient.id,
            host: recipient.host,
          }
        };

        await inbox.updateInboxPost(recipient.id, post_obj);
      }

      // Update local postData state
      setPostData({
        ...postData,
        title: updatedPost.title,
        content: updatedPost.content,
        visibility: normalizeVisibility(updatedPost.visibility) as string
      });

      closeEditModal();
    } catch (error) {
      console.error("Error updating post", error);
    }
  }

  async function handleDeletePost() {
    try {
      const postId = extractUUID(postData.id);
      await api.delete(`/api/authors/${extractUUID(authorUUID)}/posts/${postId}/`);

      const followers = await follow.getFollowers(extractUUID(authorUUID));
      const friends = await follow.getFriends(extractUUID(authorUUID));
      const target = normalizeVisibility(postData.visibility) === 1 || normalizeVisibility(postData.visibility) === 3 ? followers : friends;
      for (const recipient of target) {
        const deletedPost = {
          ...postData,
          ...(postData.type ? {} : { type: "post" }),
          follower: {
            type: "author",
            id: recipient.id,
            host: recipient.host,
          }
        };
        await inbox.deleteInboxPost(recipient.id, deletedPost);
      }

      // Update postData state to indicate deletion
      setPostData({ ...postData, visibility: "DELETED" });
      closeDeleteModal();
      onDelete(postData.id);
    } catch (error) {
      console.error("Error deleting post", error);
    }
  }

  const transformImageUri = (src: string, alt: string, title: string) => {
    return imageSrc || src;
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.profileSection}>
          <img
            className={styles.profilePic}
            src={
              profileService.getProfilePicture(postData.author)
            }
            alt={postData.author.displayName}
          />
          <div className={styles.userInfo}>
            <span className={styles.userName}>{postData.author.displayName}</span>
            <span className={styles.postTime}>{new Date(postData.published).toLocaleString()}</span>
          </div>
        </div>
        <div className={styles.icons}>
          <i className="fas fa-pencil-alt" onClick={openEditModal}></i>
          <i className="fas fa-trash-alt" onClick={openDeleteModal}></i>
        </div>
      </div>
      <div className={styles.cardContent}>
        <div className={styles.postTitle}>{postData.title}</div>

        {(postData.contentType !== ContentType.MARKDOWN && postData.contentType !== ContentType.PLAIN) ? (
          <div className={styles.cardImage}>
            <img className={styles.postImage} src={"data:image/png;base64," + postData.content} alt={postData.description} />
          </div>
        ) : (
          <div className={styles.cardContent}>
            {postData.contentType === ContentType.MARKDOWN ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                img: ({ src, alt, title }) => (
                  <img src={transformImageUri(src, alt, title)} alt={alt} title={title} className={styles.postImage}/>
                )
              }}>
                {postData.content}
              </ReactMarkdown>
            ) : (
              postData.content
            )}
          </div>
        )}
      </div>

      <div className={styles.cardFooter}>
        <div className={styles.essentials}>
          <div className={styles.icon}>
            <i className="fas fa-heart"></i>
            <span>{formatCount(postData.likes?.src ? postData.likes.src.length : 0)}</span>
          </div>
          <div className={styles.icon}>
            <i className="fas fa-comment"></i>
            <span>{formatCount(postData.comments?.src ? postData.comments.src.length : 0)}</span>
          </div>
        </div>
        <div className={styles.icon}>
          <i className="fas fa-share"></i>
        </div>
      </div>

      <EditPostModal
        isOpen={editModal}
        onRequestClose={closeEditModal}
        post={postData}
        onSubmit={handleUpdatePost}
      />

      <DeletePostModal
        isOpen={deleteModal}
        onRequestClose={closeDeleteModal}
        onDelete={handleDeletePost}
      />
    </div>
  );
}

export default MiniPostCard;
