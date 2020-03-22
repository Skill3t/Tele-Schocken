import React from "react";
import { CreateGamePage } from "./create-game/CreateGamePage";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { Container, AppBar, Toolbar, Button } from "@material-ui/core";
import "./MainPage.css";
import { PlayGamePage } from "./play-game/PlayGamePage";
import { JoinComponent } from "./JoinComponent";

interface MainPageState {
}

interface MainPageProps {
}

export class MainPage extends React.Component<MainPageProps, MainPageState> {

  public constructor(props: any) {
    super(props);
    this.state = {
      testBool: true
    }
  }


  render() {
    return (
      <Container>
        <AppBar position="static" className="main-page-header">
          <Toolbar>
            <h1 className="main-page-header-text">Tele-Schocken</h1>
          </Toolbar>
        </AppBar>
        
        <Router>
          <Switch>
            <Route exact path="/create" component={CreateGamePage} />
            <Route exact path="/play" component={PlayGamePage} />
            <Route path="" component={JoinComponent}/>
          </Switch>
        </Router>
      </Container>
    );
  }
}