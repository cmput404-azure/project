import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "../../service/config";

export default function OtherUserProfile() {
  const { userID } = useParams<{ userID: string }>();
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // fetch teh other user data using the userID
    async function fetchOtherUserData() {
      try {
        const response = await api.get(`/api/authors/${userID}/`);
        setUserData(response.data);
      } catch (error) {
        console.log("Error getting user data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchOtherUserData();
  }, []);

  // user data si still being fetched
  if (loading) return <p>Loading...</p>;
  // user data is not found
  if (!userData) return <p>User data not found</p>;

  return (
    <div>
      <h1>Other user display name: {userData.displayName}</h1>
    </div>
  );
}
