import React from "react";
import { Button, Container } from "@material-ui/core";
import "./JoinComponent.css";

interface JoinComponentState {
  testBool: boolean;
}

interface JoinComponentProps {
  testBool: boolean;
}

export class JoinComponent extends React.Component<JoinComponentProps, JoinComponentState> {

  public constructor(props: any) {
    super(props);
    this.state = {
      testBool: true
    }
  }

  render() {
    return (
      <Container>
        <Container className="join-component-button-area">
          <Container className="join-component-button-area-row">
            <Button color="primary">
              New Game!
            </Button>
          </Container>
          <Container className="join-component-button-area-row">
            <Button color="primary">
              Beitreten
            </Button>
          </Container>
        </Container>
      </Container>

    );
  }
}