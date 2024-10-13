import React from 'react';
import logo from './logo.svg';
import styles from './App.module.scss';
import ListItem from './components/ListItem/ListItem';

export default function App() {
  return (
    <div className={styles.App}>
      Social distribution

      <ListItem isRequest={true} isPost={false} isLike = {false} isFollowerList={false} />
      <ListItem isRequest={false} isPost={true} isLike = {false} isFollowerList={false} />
      <ListItem isRequest={false} isPost={false} isLike = {false} isFollowerList={true} />
      <ListItem isRequest={false} isPost={true} isLike = {true} isFollowerList={false} />

    </div>


  );
}

