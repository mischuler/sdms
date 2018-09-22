import React, { Component } from 'react'
import GoogleMapReact from 'google-map-react'
import config from  "../config"
import "./Mapitem.css"
import MapHelper from "./MapHelper.js";
import {K_SIZE} from "./MapHelper.js";


const AnyReactComponent = ({ text }) => <div>{ text }</div>;

export default class Map extends Component {
    constructor(props) {
        super(props);
    
        this.state = {
            center: { lat: 40.7446790, lng: -73.9485420 },
            zoom: 5
        }

        this.updateView = this.updateView.bind(this);
        this.renderMarkers = this.renderMarkers.bind(this);

    }
    
    updateView = change => {
        this.setState({
            center: change.center,
            zoom: change.zoom
        });
    }
    
    renderMarkers() {
        
        var markers = {}
        
        markers = this.props.inputProps.resultsArray.map((m) => {
            
            return (
            <AnyReactComponent
                key={m['checksum']}
                lat={m['lat']}
                lng={m['lng']}
                text={m['address']}
            />
            );
        });
        
        console.log("show markers");
        console.log(markers);
        console.log(this.props.inputProps);
        return markers;
    }
           

  render() {
      console.log("map it up!")
    return (
      <div className='mapitem'  style={{height: '500px', width: 'auto'}}>
        <GoogleMapReact
          bootstrapURLKeys={{ key: config.google.KEY }}
          center={ this.state.center }
          zoom={ this.state.zoom }
          hoverDistance={ K_SIZE / 2}
          >
            {this.renderMarkers()}
        </GoogleMapReact>
      </div>
    )
  }
}