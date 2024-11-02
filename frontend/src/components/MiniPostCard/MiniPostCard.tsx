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
import remarkGfm from 'remark-gfm';
import styles from "./MiniPostCard.module.scss";

interface MiniPostCardProps {
  post: PostData;
  authorUUID: string;
}


function MiniPostCard({ post, authorUUID }: MiniPostCardProps) {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [imageSrc, setImageSrc] = useState<string | null>(null);

  // Toggle modals
  const openEditModal = () => setIsEditModalOpen(true);
  const closeEditModal = () => setIsEditModalOpen(false);
  const openDeleteModal = () => setIsDeleteModalOpen(true);
  const closeDeleteModal = () => setIsDeleteModalOpen(false);

  // Handle image extraction for Markdown content
  useEffect(() => {
    const fetchImage = async () => {
      if (post.contentType === ContentType.MARKDOWN) {
        const imageRegex = /!\[.*?\]\((.*?)\)/; // Regex to find the image URL in the Markdown
        const match = post.content.match(imageRegex);
        if (match) {
          const imageUrl = match[1]; // Get the URL from the Markdown
          console.log("imageURL: ", imageUrl);

          // Check if the imageUrl is a data URL
          if (imageUrl.startsWith("data:")) {
            // Directly set the src to the data URL
            setImageSrc(imageUrl);
          } else {
            // If it's not a data URL, fetch from the endpoint
            try {
              const response = await fetch(imageUrl);
              console.log(response);
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
  }, [post.content, post.contentType]);

  // Handle update post
  async function handleUpdatePost(updatedPost: {
    title: string;
    content: string;
    visibility: number;
  }) {
    try {
      const postId = extractUUID(post.id);
      await api.put(`/api/authors/${extractUUID(authorUUID)}/posts/${postId}/`, updatedPost);

      const followers = await follow.getFollowers(authorUUID);
      const friends = await follow.getFriends(authorUUID);
      const target = updatedPost.visibility === 1 || updatedPost.visibility === 3 ? followers : friends;
      for (const recipient of target) {
        await inbox.updateInboxPost(
          recipient.id, postId, updatedPost.title, updatedPost.content, updatedPost.visibility
        );
      }

      closeEditModal();
    } catch (error) {
      console.error("Error updating post", error);
    }
  }

  // Handle delete post
  async function handleDeletePost() {
    try {
      const postId = extractUUID(post.id);
      await api.delete(`/api/authors/${authorUUID}/posts/${postId}/`);

      const followers = await follow.getFollowers(authorUUID);
      const friends = await follow.getFriends(authorUUID);
      const target = post.visibility === 1 || post.visibility === 3 ? followers : friends;
      for (const recipient of target) {
        await inbox.deleteInboxPost(recipient.id, postId);
      }

      closeDeleteModal();
    } catch (error) {
      console.error("Error deleting post", error);
    }
  }

  const transformImageUri = (src: string, alt: string, title: string) => {
    return imageSrc || src; // Return the fetched Base64 string if available, otherwise the original src
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.profileSection}>
          <img
            className={styles.profilePic}
            src={
              post.author.profileImage ??
              `https://ui-avatars.com/api/?background=random&name=${post.author.displayName}`
            }
            alt={post.author.displayName}
          />
          <div className={styles.userInfo}>
            <span className={styles.userName}>{post.author.displayName}</span>
            <span className={styles.postTime}>{post.published}</span>
          </div>
        </div>
        <div className={styles.icons}>
          <i className="fas fa-pencil-alt" onClick={openEditModal}></i>
          <i className="fas fa-trash-alt" onClick={openDeleteModal}></i>
        </div>
      </div>

      {(post.contentType !== ContentType.MARKDOWN && post.contentType !== ContentType.PLAIN) ? (
        <div className={styles.cardImage}>
          <img className={styles.postImage} src={"data:image/png;base64,"+post.content} alt={post.description} />
        </div>
      )
        : (
          <>
            <div className={styles.cardSummary}>{post.title}</div>
            <div className={styles.cardContent}>
              {post.contentType === ContentType.MARKDOWN ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                  img: ({ src, alt, title }) => {
                    return (
                      <img src={transformImageUri(src, alt, title)} alt={alt} title={title} />
                    );
                  }
                }}>
                  {post.content}
                </ReactMarkdown>
              ) : (
                post.content
              )}
            </div>
          </>
        )
      }



      <div className={styles.cardFooter}>
        <div className={styles.essentials}>
          <div className={styles.icon}>
            <i className="fas fa-heart"></i>
            <span>{formatCount(post.likes.src.length)}</span>
          </div>
          <div className={styles.icon}>
            <i className="fas fa-comment"></i>
            <span>{formatCount(post.comments.src.length)}</span>
          </div>
        </div>
        <div className={styles.icon}>
          <i className="fas fa-share"></i>
        </div>
      </div>

      <EditPostModal
        isOpen={isEditModalOpen}
        onRequestClose={closeEditModal}
        post={post}
        onSubmit={handleUpdatePost}
      />

      <DeletePostModal
        isOpen={isDeleteModalOpen}
        onRequestClose={closeDeleteModal}
        onDelete={handleDeletePost}
      />
    </div>
  );
}

export default MiniPostCard;
