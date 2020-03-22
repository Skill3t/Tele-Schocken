import React from "react";
import {Button, Container} from "@material-ui/core";

interface CreateGamePageState{
  testBool: boolean;
}

interface CreateGamePageProps {
  testBool: boolean;
}

export class CreateGamePage extends React.Component<CreateGamePageProps, CreateGamePageState> {

  public constructor(props:any){
    super(props);
    this.state={
      testBool: true
    }
  }

  render(){
    return(
      <Container>
        <h2>Create new Game</h2>
      </Container>
      
    );
  }
}