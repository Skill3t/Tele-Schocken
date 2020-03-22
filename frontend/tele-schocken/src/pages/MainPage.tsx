import React from "react";
import { CreateGamePage } from "./create-game/CreateGamePage";
import {BrowserRouter as Router, Switch, Route} from "react-router-dom";
import { Container, AppBar, Toolbar } from "@material-ui/core";
import "./MainPage.css";
import { PlayGamePage } from "./game/PlayGamePage";

interface MainPageState{
}

interface MainPageProps {
}

export class MainPage extends React.Component<MainPageProps, MainPageState> {

  public constructor(props:any){
    super(props);
    this.state={
      testBool: true
    }
  }


  render(){
    return(
      <div >
        <AppBar position="static" className="main-page-header">
          <Toolbar>
            <h1 className="main-page-header-text">Tele-Schocken</h1>
          </Toolbar>
        </AppBar>
        <Router>
          <Switch>
            <Route exact path="/create" component={CreateGamePage}/> 
            <Route exact path="/play" component={PlayGamePage} />
          </Switch>
        </Router>
      </div>
    
    );
  }
}