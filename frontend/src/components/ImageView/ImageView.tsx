import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../service/config";
import styles from './ImageView.module.scss';

const ImageView = () => {
  const { postID } = useParams();
  const [imageSrc, setImageSrc] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchImage = async () => {
      try {
        // Call local image backend, handle remote posts there
        const response = await api.get<{"image": string, "content_type": string}>(`${process.env.REACT_APP_API_BASE_URL}/api/posts/` + encodeURIComponent(postID) + "/image");
        const json = response.data;
        setImageSrc(json.image);
      } catch (err) {
        setError("Failed to load image");
        console.error(err);
      }
    };

    fetchImage();
  }, [postID]);

  if (error) {
    return <div>{error}</div>;
  }

  if (!imageSrc) {
    return <div>Loading...</div>;
  }

  return (
    <div className={styles.container}>
      <img src={imageSrc} alt="Post" className={styles.container__image} />
    </div>
  );
};

export default ImageView;
