import React, { Component } from "react";
import {FormGroup, FormControl, ControlLabel } from "react-bootstrap";
import LoaderButton from "../components/LoaderButton";
import "./Home.css";
import DatePicker from 'react-datepicker';
import moment from 'moment';
import PlacesAutocomplete from 'react-places-autocomplete';
import { searchAssets } from "../libs/awsLib";

import 'react-datepicker/dist/react-datepicker.css';
 
// CSS Modules, react-datepicker-cssmodules.css
import 'react-datepicker/dist/react-datepicker-cssmodules.css';
 

export default class Search extends Component {
    constructor(props) {
        super(props);
        

        this.state = {
            isLoading: false,
            freeText: "",
            startDate: null,
            endDate: null,
            radius: 5,
            address: ''
        };
            
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleStartDateChange = this.handleStartDateChange.bind(this);
        this.handleEndDateChange = this.handleEndDateChange.bind(this);
        this.handleLocationChange = this.handleLocationChange.bind(this);
    }
    
    // Basic change handling
    handleChange = event => {
        this.setState({ [event.target.id]: event.target.value });
    }
    
    // Location change needed because event.id cannot be taken from places object
    handleLocationChange = address => {
        console.log("The address has been changed: " + address);
        this.setState({ address: address });
    }
    
    // I need two separate handlers for each piece of the date range
    handleStartDateChange = date => {
        this.setState({ startDate: date });
    }

    handleEndDateChange = date => {
        this.setState({ endDate: date });
    }
  
    // 
    handleSubmit = async event => {
        event.preventDefault();
        console.log(event);
        var searchResults = {};
        // Construct the query string for AWS search
       
        var queryStatement = {
            accountId: 'account1', // Dummy
            groupId: 'group1', // Dummy
            caseId: '999', // Dummy
            freeText: this.state.freeText,
            radius: this.state.radius
        };
        
        if (this.state.startDate != null) {
            queryStatement['startDate'] = this.state.startDate.format("MM/DD/YYYY");
        }
            
        if (this.state.endDate != null) {
            queryStatement['endDate'] = this.state.endDate.format("MM/DD/YYYY");
        }
       
        if (this.state.address !== '') {
            queryStatement['address'] = this.state.address
        }
        
        console.log(queryStatement);
       
        this.setState({ isLoading: true });
        
        // Submit to the search API and load the Payload as a JSON object
        try {
            
            var resultSet;
            resultSet = await searchAssets(queryStatement);
            if (resultSet['StatusCode'] !== 200) {
                console.log("Error in lambda function");
            }

            searchResults = JSON.parse(resultSet['Payload'])
            console.log(searchResults);
            // This will send the results to parent object
            this.props.inputProps.onChange(searchResults);
            
            this.setState({
                isLoading: false,
            });
        
        }
        catch (e) {
            console.log(e);
            this.setState({ isLoading: false });
        }
    }
    
    render() {
        
        const autoLocationProps = {
          value: this.state.address,
          onChange: this.handleLocationChange,
        }
        
        console.log(this.state);
        
        // Only fetch suggestions when the input text is longer than 3 characters.
        const shouldFetchSuggestions = ({ value }) => value.length > 3
        
        
        return (
            <div className="Search">
                <form onSubmit={this.handleSubmit}>
                    <FormGroup controlId="freeText" bsSize="large">
                        <ControlLabel>Enter text to search on</ControlLabel>
                        <FormControl
                            type="textarea"
                            onChange={this.handleChange}
                            value={this.state.freeText}
                            placeholder="Enter any values to search on"
                        />
                    </FormGroup>
                    <FormGroup controlId="address" bsSize="large">
                        <ControlLabel>Enter search location</ControlLabel>
                        <PlacesAutocomplete 
                            inputProps={autoLocationProps}
                            shouldFetchSuggestions={shouldFetchSuggestions}
                            placeholderText="Start typing an address"
                        />
                    </FormGroup>
                    <FormGroup controlId="radius" bsSize="large">
                        <ControlLabel>Enter search radius</ControlLabel>
                        <FormControl
                            onChange={this.handleChange}
                            type="text"
                            value={this.state.radius}
                        />
                    </FormGroup>
                    <FormGroup controlId="startDate" bsSize="large">
                        <ControlLabel>Enter start date</ControlLabel>
                        <DatePicker
                            onChange={this.handleStartDateChange}
                            selected={this.state.startDate}
                            placeholderText="Enter start date"
                            isClearable={true}
                            maxDate={this.state.endDate}
                        />
                    </FormGroup>
                        <FormGroup controlId="endDate" bsSize="large">
                        <ControlLabel>Enter end date</ControlLabel>
                        <DatePicker
                            onChange={this.handleEndDateChange}
                            selected={this.state.endDate}
                            placeholderText="Enter end date"
                            isClearable={true}
                            minDate={this.state.startDate}
                        />
                    </FormGroup>
                    <LoaderButton
                        block
                        bsSize="large"
                        type="submit"
                        isLoading={this.state.isLoading}
                        text="Search for files"
                        loadingText="Searching..."
                    />
                </form>
            </div>
        );
    }
}