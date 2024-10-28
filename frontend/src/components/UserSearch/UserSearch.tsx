// @ts-nocheck

import "@fortawesome/fontawesome-free/css/all.min.css";

import React, { useEffect, useState } from 'react';
import { useAuth } from "../../state";


import ListItem from "../ListItem/ListItem";
import { api } from "../../service/config";
import styles from "./UserSearch.module.scss";


interface userSearchProps {
  closeModal?: () => void;
}

export default function UserSearch({ closeModal }: userSearchProps) {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [results, setResults] = useState<any[]>([]); // Change 'any' to the appropriate type based on your API response
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const authProvider = useAuth();

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

    // Filter results based on the search term
  const filteredResults = results.filter((user) =>
    user.displayName.toLowerCase().includes(searchTerm.toLowerCase())
  );   

  // Fetch users when the search term changes
 useEffect(() => {
        const fetchUsers = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await api.get(`/api/authors/all/`,{
                    params: { user: authProvider.user.uuid }
                }); 
                console.log("RESPONSE", response.data);
                setResults(response.data); 
            } catch (err) {
                console.error('Error fetching users:', err);
                setError('Failed to fetch users');
            } finally {
                setLoading(false);
            }
        };

    fetchUsers();
  }, []);

  return (
    <div className={styles.componentWidth}>
      <div className={styles.searchContainer}>
        <i className="fa-solid fa-magnifying-glass"></i>
        <input
          className={styles.searchInput}
          type="text"
          placeholder="Search..."
          value={searchTerm}
          onChange={handleInputChange}
        />
      </div>


      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      {filteredResults.length > 0 ? (
        <ul className={styles.ul}>
          {filteredResults.map((user) => (
            <ListItem
              key={user.id}
              isRequest={false}
              isPost={false}
              isLike={false}
              isFollowerList={false}
              isUserList={true}
              user={user}
              closeModal={closeModal}
            />
          ))}
        </ul>
      ) : (
        searchTerm && <p>No users found</p> // Show message when there are no matches
      )}
    </div>
  );
}
