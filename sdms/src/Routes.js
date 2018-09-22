import React from "react";
import { Route, Switch } from "react-router-dom";
import Home from "./containers/Home";
import NotFound from "./containers/NotFound";
import Upload from "./containers/Upload";
import AppliedRoute from "./components/AppliedRoute";
import Search from "./containers/Search";
import Viewfiles from "./containers/Viewfiles";
import Viewmap from "./containers/Viewmap";

export default ({ childProps }) =>
  <Switch>
    <AppliedRoute path="/" exact component={Home} props={childProps} />
    <AppliedRoute path="/upload" exact component={Upload} props={childProps} />
    <AppliedRoute path="/search" exact component={Search} props={childProps} />
    <AppliedRoute path="/viewfiles" exact component={Viewfiles} props={childProps} />
    <AppliedRoute path="/viewmap" exact component={Viewmap} props={childProps} />

    { /* Catch all unmatched routes */ }
        <Route component={NotFound} />
  </Switch>;