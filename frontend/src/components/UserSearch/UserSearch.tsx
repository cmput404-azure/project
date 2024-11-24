// @ts-nocheck

import "@fortawesome/fontawesome-free/css/all.min.css";

import React, { useEffect, useState } from 'react';

import { CircularProgress } from "@mui/material";
import ListItem from "../ListItem/ListItem";
import { api } from "../../service/config";
import styles from "./UserSearch.module.scss";
import { useAuth } from "../../state";

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
        if (authProvider.isAuthenticated === false) {
          const response = await api.get(`/api/authors/all/`, {
            params: { user: "anonymous" }
          });
          setResults(response.data);
        } else {
          const response = await api.get(`/api/authors/all/`, {
            params: { user: authProvider.user.uuid }
          });
          setResults(response.data);
        }

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
    <div className={styles.user__search}>
      <div className={styles.search__container}>
        <input
          className={styles.search__input}
          type="text"
          placeholder="Search users..."
          value={searchTerm}
          onChange={handleInputChange}
        />
      </div>

      <div className={styles.results__container}>
        {loading ? (
          <div className={"loading_component"}>
            <CircularProgress sx={{ color: "#70ffaf" }} />
          </div>
        ) : error ? (
          <p className={styles.error}>{error}</p>
        ) : (
          <div className={styles.results__list}>
            {filteredResults.length === 0 ? (
              <p className={styles.no__results}>No users found</p>
            ) : (
              filteredResults.map((user) => (
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
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}