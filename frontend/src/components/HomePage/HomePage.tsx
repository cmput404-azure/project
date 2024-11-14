import { Button, CircularProgress } from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import PeopleIcon from "@mui/icons-material/People";
import { useEffect, useState } from "react";
import { useAuth } from "../../state";
import { api } from "../../service/config";
import author from "../../service/author";
import setting from "../../service/setting";
import stream from "../../service/stream";
import { Author, RemoteFollowRequest } from "../../models/models";
import Post from "../Post/Post";
import PostBar from "../PostBar/PostBar";
import styles from "./HomePage.module.scss";
import AuthorPost from "../AuthorPost/AuthorPost";
import remote from "../../service/remote";

type ViewType = "all" | "unlisted_friends-only";

const HomePage = () => {
  const [recommended, setRecommended] = useState<Author[]>([]); // list of remote authors for now, but should make it local if no remote connection, and make sure it's only people
  const [publicPosts, setPublicPosts] = useState<any[]>([]);
  const [privatePosts, setPrivatePosts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<any>(null);
  const [activeFilterPost, setActiveFilterPost] = useState<ViewType>("all");
  const [publicPage, setPublicPage] = useState(1); // so we can use the pagination feature
  const [privatePage, setPrivatePage] = useState(1);
  const [totalPublicPages, setTotalPublicPages] = useState(0);
  const [totalPrivatePages, setTotalPrivatePages] = useState(0);
  const pageSize = 15;
  const authProvider = useAuth();

  const [isUserLoading, setIsUserLoading] = useState(true);

  // Function to randomly select authors from an array
  const selectRandomAuthors = (authors: Author[], minCount: number, maxCount: number): Author[] => {
    const count = Math.floor(Math.random() * (maxCount - minCount + 1)) + minCount;
    const shuffled = authors.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  };

  useEffect(() => {
    const fetchUser = async () => {
      if (!authProvider.user) {
        setIsUserLoading(false); // user not authenticated
        return;
      }

      try {
        const authorReq = await api.get(
          `/api/authors/${authProvider.user.uuid}/`
        );
        setUser(authorReq.data);
        setIsUserLoading(false);
      } catch (err) {
        console.log(err);
        setError("Failed to fetch user data.");
        setIsUserLoading(false);
      }
    };

    const fetchRecommended = async () => {
      try {
        if (!authProvider.user) {
          setIsUserLoading(false); // user not authenticated
          return;
        }
        const fetchedData = await setting.getNodeList();

        const allRemoteAuthors: Author[] = [];

        for (const node of fetchedData) {
          const fetchRemoteAuthors = async (host: string, username: string, password: string) => {
            let page = 1;
            const size = 3; // just need a little for recommended section

            const authors = author.getNodeAuthors(host, username, password, page, size);
            return authors;
          }

          if (node.is_authenticated) {
            const nodeAuthors = await fetchRemoteAuthors(node.host, node.username, node.password);
            allRemoteAuthors.push(...nodeAuthors);
          }
        }

        // We randomly select from the list of all remote authors
        // If we're connected to multiple remote authors, we don't want to only recommend authors from one remote node
        const randomAuthors = selectRandomAuthors(allRemoteAuthors, 3, 3);
        setRecommended(randomAuthors);
        
      } catch (err) {
        console.error("Something went wrong: ", err);
      }
    }
    
    fetchUser();
    fetchRecommended();
  }, [authProvider.user]); // This effect runs when authProvider.user changes

  const fetchPosts = async (
    publicPage = 1,
    privatePage = 1,
  ) => {
    if (isUserLoading) return;
  
    try {
      const publicResponse = await stream.getStream(false, publicPage);
      const privateResponse = await stream.getStream(true, privatePage);
      
      setPublicPosts(prevPosts => {
        const existingIds = new Set(prevPosts.map(post => post.id));
        const newPublicPosts = publicResponse.src.filter(post => !existingIds.has(post.id));
        const latestExistingDate = new Date(Math.max(...prevPosts.map(post => new Date(post.published).getTime())));
        const newerPosts = newPublicPosts.filter(post => new Date(post.published).getTime() > latestExistingDate.getTime()); // the ones created from PostBar
        const filteredPosts = newPublicPosts.filter(post => !newerPosts.some(newPost => newPost.id === post.id)); // don't want duplicate
        return [...newerPosts, ...prevPosts, ...filteredPosts];
      });

      setPrivatePosts(prevPosts => {
        const existingIds = new Set(prevPosts.map(post => post.id));
        const newPrivatePosts = privateResponse.src.filter(post => !existingIds.has(post.id));
        const latestExistingDate = new Date(Math.min(...prevPosts.map(post => new Date(post.published).getTime())));
        const newerPosts = newPrivatePosts.filter(post => new Date(post.published).getTime() > latestExistingDate.getTime());
        const filteredPosts = newPrivatePosts.filter(post => !newerPosts.some(newPost => newPost.id === post.id));
        return [...newerPosts, ...prevPosts, ...filteredPosts];
      });

      setTotalPublicPages(Math.ceil(publicResponse.count / pageSize));
      setTotalPrivatePages(Math.ceil(privateResponse.count / pageSize));
  
      setIsLoading(false);

    } catch (err) {
      console.log(err);
      setError("Failed to fetch posts. Please try again.");
    }
  };

  useEffect(() => {
    fetchPosts(publicPage, privatePage);
    const interval = setInterval(() => {
      fetchPosts(publicPage, privatePage);
    }, 60000);
    return () => clearInterval(interval);
  }, [isUserLoading, privatePage, publicPage]);

  // useEffect(() => {
  //   checkRemoteRequestStatus();
  //   const interval = setInterval(() => {
  //     checkRemoteRequestStatus();
  //   }, 60000);
  
  //   return () => clearInterval(interval);
  // }, []);

  const nextPublicPage = async () => {
    if (isLoading || publicPage >= totalPublicPages) return;
    setPublicPage(prevPage => prevPage + 1);
  }

  const nextPrivatePage = async () => {
    if (isLoading || privatePage >= totalPrivatePages) return;
    setPrivatePage(prevPage => prevPage + 1);
  }

  function handleFilterPost(icon: ViewType) {
    setActiveFilterPost(icon);
  }

  // Checks if any remote pending requests (locally) has been accepted remotely
  const checkRemoteRequestStatus = async () => {
    if (!authProvider.user) {
      return;
    }

    try {
      const requests: RemoteFollowRequest[] = await remote.checkRequestStatus(authProvider.user.uuid);
      for (let request of requests) {
        // Check if follow request is accepted
        const isFollower = remote.checkRemoteNode(
          request.remote_object.host,
          request.remote_object.id,
          request.actor.host,
          request.actor.id
        );

        if (isFollower) {
          await remote.setRequestAsAccepted(
            authProvider.user.uuid,
            request.remote_object.host,
            request.remote_object.id
          );

          await remote.deleteStaleRequest(
            authProvider.user.uuid,
            request.remote_object.host,
            request.remote_object.id
          );
        }
      }
    } catch (error) {
      console.error('Error fetching follow requests:', error);
    }
  }

  if (isLoading)
    return (
      <div className={"loading"}>
        <CircularProgress sx={{ color: "#70ffaf" }} />
      </div>
    );
  if (error) return <p>{error}</p>;

  const displayedPosts = activeFilterPost === "all" ? publicPosts : privatePosts;

  return (
    <div className={styles.homePage}>
      {/* First Section: PostBar and Post Card */}
      <div className={styles.postSection}>
        <PostBar fetchPosts={fetchPosts} author={user} />
        {authProvider.isAuthenticated && (
          <div className={styles.icon_bar}>
            <div
              className={`${styles.icon_section} ${
                activeFilterPost === "all" ? styles.active : ""
              }`}
              onClick={() => handleFilterPost("all")}
            >
              <PublicIcon className={styles.icon} />
            </div>
            <div
              className={`${styles.icon_section} ${
                activeFilterPost === "unlisted_friends-only"
                  ? styles.active
                  : ""
              }`}
              onClick={() => handleFilterPost("unlisted_friends-only")}
            >
              <PeopleIcon className={styles.icon} />
            </div>
          </div>
        )}
        {displayedPosts.map((post) => (
          <Post
            key={post.type === "shared" ? `${post.id}-${post.shared_by}` : post.id}
            postGiven={post}
            canToggleComments={false}
          />
        ))}
        {displayedPosts.length === 0 && (
          <div className={styles.noPosts}>
            <p>There are no posts on this node 🫨</p>
          </div>
        )}
        {activeFilterPost === "all" && publicPage < totalPublicPages && (
          <Button
            variant="contained"
            onClick={nextPublicPage}
            disabled={isLoading}
            sx={{ marginTop: "1rem", backgroundColor: "#70ffaf", color: "black" }}
          >
            {isLoading ? <CircularProgress size={24} sx={{ color: "#70ffaf" }} /> : "Load More"}
          </Button>
        )}

        {activeFilterPost === "unlisted_friends-only" && privatePage < totalPrivatePages && (
          <Button
            variant="contained"
            onClick={nextPrivatePage}
            disabled={isLoading}
            sx={{ marginTop: "1rem", backgroundColor: "#70ffaf", color: "black" }}
          >
            {isLoading ? <CircularProgress size={24} sx={{ color: "#70ffaf" }} /> : "Load More"}
          </Button>
        )}
      </div>


      {authProvider.isAuthenticated && <div className={styles.authorSection}>
          <h2 className={styles.recommendedTitle}>Recommended for you</h2>
          {recommended.map((author) => (
            <AuthorPost key={author.id} author={author}/>
          ))}
      </div>}
    </div>
  );
};

export default HomePage;
