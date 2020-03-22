import React from 'react';
import logo from './logo.svg';
import './App.css';
import { CreateGamePage } from './pages/create-game/CreateGamePage';
import { MainPage } from './pages/MainPage';
import "typeface-roboto";
import { AppBar } from '@material-ui/core';

function App() {

  
  return (
    <div className="App">
     
      <MainPage />
    </div>
  );
}

export default App;
