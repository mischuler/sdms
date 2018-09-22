import { withGoogleMap, GoogleMap, Marker } from "react-google-maps"
import React from "react";

export default withGoogleMap(({
    defaultZoom,
    defaultCenter,
    isMarkerShown,
    ...props
    
}
    ) =>
  <GoogleMap
    defaultZoom={props.defaultZoom}
    defaultCenter={props.defaultCenter}
  >
    {props.isMarkerShown && <Marker position={{ lat: -34.397, lng: 150.644 }} />}
  </GoogleMap>
  )