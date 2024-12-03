import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../service/config";
import styles from './ImageView.module.scss';
import { normalizeURL } from "../../util/formatting/normalizeURL";

const ImageView = () => {
  const { postID } = useParams();
  const [imageSrc, setImageSrc] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchImage = async () => {
      try {
        const host = normalizeURL(process.env.REACT_APP_API_BASE_URL);
        // Call local image backend, handle remote posts there
        const response = await api.get<string>(`${host}/api/posts/` + encodeURIComponent(postID) + "/image");
        setImageSrc(response.data); // base64 string
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
