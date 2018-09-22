import React, { Component } from "react";
import { Link } from "react-router-dom";
import { Navbar, Nav } from "react-bootstrap";
import RouteNavItem from "./components/RouteNavItem";
import Routes from "./Routes";
import "./App.css";

class App extends Component {
    
  constructor(props) {
      super(props);
      
      this.state = {
          isAuthenticated: false
      };
  }
  
  userHasAuthenticated = authenticated => {
      this.setState({ isAuthenticated: authenticated });
  }
    
  render() {
    const childProps = {
        isAuthenticated: this.state.isAuthenticated,
        userHasAuthenticated: this.userHasAuthenticated
    };
    return (
      <div className="App container">
        <Navbar fluid collapseOnSelect>
          <Navbar.Header>
            <Navbar.Brand>
              <Link to="/">SDMS</Link>
              </Navbar.Brand>
            <Navbar.Toggle />
          </Navbar.Header>
          <Navbar.Collapse>
            <Nav pullRight>
                <RouteNavItem href="/upload">Upload file</RouteNavItem>
                <RouteNavItem href="/viewfiles">View Files</RouteNavItem>
                <RouteNavItem href="/viewmap">View Map</RouteNavItem>
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        <Routes childProps={childProps} />
      </div>
    );
  }
}

export default App;