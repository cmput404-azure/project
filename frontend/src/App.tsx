import React from 'react';
import logo from './logo.svg';
import styles from './App.module.scss';
import ListItem from './components/ListItem/ListItem';


export default function App() {
  return (
    <div className={styles.App}>
      Social distribution
      <ListItem></ListItem>

    </div>
  );
}

