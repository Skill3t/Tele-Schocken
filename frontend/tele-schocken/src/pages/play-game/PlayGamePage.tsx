import React from "react";
import {Button, Container} from "@material-ui/core";

interface PlayGamePageState{
  testBool: boolean;
}

interface PlayGamePageProps {
  testBool: boolean;
}

export class PlayGamePage extends React.Component<PlayGamePageProps, PlayGamePageState> {

  public constructor(props:any){
    super(props);
    this.state={
      testBool: true
    }
  }

  render(){
    return(
      <Container>
        <h2> play the game</h2>
      </Container>
      
    );
  }
}