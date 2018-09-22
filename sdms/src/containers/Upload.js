import React, { Component } from "react";
import {FormGroup, FormControl, ControlLabel } from "react-bootstrap";
import LoaderButton from "../components/LoaderButton";
import s3Upload from "../libs/awsLib";
import "./Home.css";
import deepcopy from "deepcopy";

export default class Upload extends Component {
    constructor(props) {
        super(props);
        

        {/* We'll need to create an object to pull in the "User information" */ }
        this.state = {
            isLoading: false,
            metadata: {},
            file: null
        };
            
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleFileChange = this.handleFileChange.bind(this);
    }
    
    validateForm() {
        
        var isValid = false;
        
        if (this.state.file != null) {
            isValid = true
        }
        console.log("Validation " + isValid);
        return isValid;
    }
    
    handleChange = event => {
        var M = deepcopy(this.state.metadata);
        M[event.target.id] = event.target.value
        this.setState({metadata: M})
    }
    
    handleFileChange = event => {
        this.setState({file : event.target.files[0]})
        console.log(event.target.files[0])
    }
    
    handleSubmit = async event => {
        event.preventDefault();
        console.log(event);
        console.log(this.state.file,this.state.metadata);
        
        this.setState({ isLoading: true });
        
        try {
            const uploadedFileName = this.state.file
            ? (await s3Upload(this.state.file,this.state.metadata)).Location
            : null;
            
            alert("Upload complete");
            this.setState({
                isLoading: false,
                file: null,
                metadata: {}
            });
        
        }
        catch (e) {
            alert(e);
            console.log(e);
            this.setState({ isLoading: false });
        }
    }
    
    render() {
        return (
            <div className="Upload">
                <form onSubmit={this.handleSubmit}>
                    <FormGroup controlId="file" bsSize="large">
                        <ControlLabel>Select file to upload</ControlLabel>
                        <FormControl
                            autoFocus
                            type="file"
                            onChange={this.handleFileChange}
                        />
                    </FormGroup>
                    <FormGroup controlId="user_description" bsSize="large">
                        <ControlLabel>Enter a file description</ControlLabel>
                        <FormControl
                            onChange={this.handleChange}
                            type="textarea"
                        />
                    </FormGroup>
                    <LoaderButton
                        block
                        bsSize="large"
                        disabled={!this.validateForm()}
                        type="submit"
                        isLoading={this.state.isLoading}
                        text="Upload File"
                        loadingText="Uploading file..."
                    />
                </form>
            </div>
        );
    }
}