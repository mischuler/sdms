import React, { Component } from "react";
import {Image} from "react-bootstrap"
import Search from "./Search";
import "./Home.css";
import config from "../config";
import MapItem from "../components/MapItem";
import PickPlayer from '../components/PickPlayer';

const AnyReactComponent = ({ text }) => <div>{text}</div>;

export default class Viewmap extends Component {
    constructor(props) {
        super(props);
        
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
        this.updatePlayer = this.updatePlayer.bind(this);
        this.updatePlayerInfo = this.updatePlayerInfo.bind(this);
    }

    updateResults = results => {
        this.setState({ searchResults: results });
    }
    
    updatePlayer = show => {
        this.setState({showPlayer: show})
    }
    
    updatePlayerInfo = data => {
        this.setState({
            assetClass: data.assetClass,
            fileURL: data.fileURL,
            playbackURL: data.playbackURL,
            fileName: data.fileName,
            description: data.description,
            thumbnail: data.thumbnail        
        });
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
    
    renderMap(searchResults) {
        
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
                    'description': hit['_source']['UserFields']['description'],
                    'dateRecorded': hit['_source']['General']['recorded_date'],
                    'PDL': config.CDN.URL + hit['_source']['Filename'] + hit['_source']['PDL'],
                    'thumbnail': config.CDN.URL + hit['_source']['Filename'] + hit['_source']['thumbnail'],
                    'fileURL': config.CDN.URL + hit['_source']['Filename'] + '/' + hit['_source']['Filename'] + hit['_source']['Extension'],
                    'fileName': hit['_source']['Filename'],
                    'lat': hit['_source']['General']['Latitude'],
                    'lng': hit['_source']['General']['Longitude']
                };
            });
            
            const mapProps = {
                resultsArray: newResults,
                onChange: this.updatePlayerInfo,
                onPlay: this.updatePlayer
            };            
            
            return (
                <div className="map">
                    <hr/>
                    {hits} files returned in {took} milliseconds
                    <hr/>
                 <MapItem 
                    inputProps={mapProps}
                 />
                </div>
            );
        
        }
    }
    
    render() {   
        console.log(this.state);
        // Eventually we will render the results in the table...
        return (
            <div className="Viewmap">
            {this.renderSearchForm()}
            {this.renderMap(this.state.searchResults)}
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