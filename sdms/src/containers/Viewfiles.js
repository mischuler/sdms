import React, { Component } from "react";
import {Image} from "react-bootstrap"
import Search from "./Search";
import "./Home.css";
import BootstrapTable from 'react-bootstrap-table-next';
import '../../node_modules/react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import config from "../config";
import PickPlayer from '../components/PickPlayer';
import moment from "moment";

export default class Viewfiles extends Component {
    constructor(props) {
        super(props);
        
        // move these to input props?
        this.state = {
            searchResults: null,
            assetClass: null,
            fileURL: null,
            playbackURL: null,
            showPlayer: false,
            fileName: null,
            description: null,
            thumbnail: null
        };
        
        this.updateResults = this.updateResults.bind(this);
    }
    
    updatePlayer = show => {
        this.setState({showPlayer: show})
    }

    updateResults = results => {
        this.setState({ searchResults: results });
    }

    renderSearchForm() {
    
         const searchProps = {
          value: this.state.searchResults,
          onChange: this.updateResults
        };
    
        return (
            <div className="SearchForm">
                <Search
                    inputProps={searchProps}
                />
            </div>
        )
    };
    
    formatThumbnail(cell, row) {
        return (<Image src={cell} thumbnail responsive />)
    };
    
    formatDate(cell, row) {
        var date = moment(cell, moment.ISO_8601).format("YYYY-DD-MM HH:MM Z");
        return (date)
    };
    
    renderTable(searchResults) {
        
        if (searchResults == null) {
            return "";
        } else {
            
            
            
            // Get the request information
            const hits = searchResults['hits']['total'];
            const took = searchResults['took'];
            // Because we need to pass the data into the bootstrap table
            // we need to "re-configure" the hits
            var newResults = {};
            newResults = searchResults['hits']['hits'].map((hit) => {
                return {
                    'checksum': hit['_source']['checksum'],
                    'assetClass': hit['_source']['Asset_Class'],
                    'address': hit['_source']['General']['Address'],
                    'makemodel': hit['_source']['General']['make'] + ' ' + hit['_source']['General']['model'],
                    'description': hit['_source']['UserFields']['description'],
                    'dateRecorded': hit['_source']['General']['recorded_date'],
                    'PDL': config.CDN.URL + hit['_source']['Filename'] + hit['_source']['PDL'],
                    'thumbnail': config.CDN.URL + hit['_source']['Filename'] + hit['_source']['thumbnail'],
                    'dateImported': hit['_source']['Imported_Time'],
                    'fileURL': config.CDN.URL + hit['_source']['Filename'] + '/' + hit['_source']['Filename'] + hit['_source']['Extension'],
                    'fileName': hit['_source']['Filename']
                };
            });
            
            const columns = [{
                dataField: 'checksum',
                text: 'checksum',
                hidden: true
            } ,{
                dataField: 'thumbnail',
                text: 'Thumbnail',
                formatter: this.formatThumbnail
            },{
                dataField: 'PDL',
                text: 'PDL',
                hidden: true
            } , {
                dataField: 'assetClass',
                text: 'Asset Class',
                sort: true
            } , {
                dataField: 'address',
                text: 'Address'
            }, {
                dataField: 'description',
                text: 'Description'
            }, {
                dataField: 'dateImported',
                text: 'Imported',
                formatter: this.formatDate,
                sort: true
            }, {
                dataField: 'dateRecorded',
                text: 'Recorded',
                formatter: this.formatDate,
                sort: true
            }, {
                dataField: 'makemodel',
                text: 'Make / Model'
            }];
            
            const rowEvents = {
                onClick: (e, row, rowIndex) => {
                    console.log(row);                
                    this.setState({ 
                        assetClass: row['assetClass'],
                        fileURL: row['fileURL'],
                        playerURL: row['PDL'],
                        showPlayer: true,
                        fileName: row['fileName'],
                        description: row['description'],
                        thumbnail: row['thumbnail']
                    });

                }
            };
            return (
                <div className="Table">
                    <hr/>
                    {hits} files returned in {took} milliseconds
                    <hr/>
                    <BootstrapTable data={newResults} keyField='checksum' columns={columns} rowEvents={rowEvents} striped hover />
                </div>
            )
        };
    };
    
    
    render() {   

        console.log("View files state")
        console.log(this.state);
        // Eventually we will render the results in the table...
        // Render the single Modal here and update on the onclick?!?!
        return (
            <div className="Viewfiles">
            {this.renderSearchForm()}
            {this.renderTable(this.state.searchResults)}
            <PickPlayer
                assetClass={this.state.assetClass}
                fileURL={this.state.fileURL}
                playerURL={this.state.playerURL}
                show={this.state.showPlayer}
                onChange={this.updatePlayer}
                Title={this.state.fileName}
                description={this.state.description}
                thumbnail={this.state.thumbnail}
            />
            </div>
        );
    }
}