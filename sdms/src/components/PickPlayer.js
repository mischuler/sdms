import { Modal, Image, Button, Glyphicon } from "react-bootstrap"
import React, { Component } from "react";
import Lightbox from 'react-image-lightbox-rotate';
import { Player, ControlBar, ReplayControl,
  ForwardControl, CurrentTimeDisplay,
  TimeDivider, PlaybackRateMenuButton, VolumeMenuButton
} from 'video-react'; 
import "../../node_modules/video-react/dist/video-react.css"; // import css

export default class PickPlayer extends Component {
    
    constructor(props) {
        super(props);
        
        this.state = {
            TBD: null
        };
        
        this.handleClose = this.handleClose.bind(this);
        this.renderPlayer = this.renderPlayer.bind(this);
        this.handleDownload = this.handleDownload.bind(this);
    }
    
  
    handleClose() {
        this.props.onChange(false);
    }

    handleDownload() {
        console.log("Download time brotha")
        return (
            <a href={this.props.fileURL} />
            );
            
            //                    <Button onClick={this.handleDownload}>
//                        <Glyphicon glyph="cloud-download" /> Download file
  //                  </Button>

    }
    
    renderPlayer() {
        
        console.log("prepare switch: ")
        console.log(this.props)
        
        switch(this.props.assetClass) {
            case "Image":
                console.log("Image")
                return (
                this.props.show && (
                    <Lightbox
                        mainSrc={this.props.fileURL}
                        onCloseRequest={this.handleClose}
                        imageTitle={this.props.Title}
                        imageCaption={this.props.description}
                     />
                     )
                );
                
            
            case "Video":
                return (
                <Modal show={this.props.show} onHide={this.handleClose}>
                    <Modal.Header closeButton>
                        <Modal.Title>{this.props.description}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Player
                            poster={this.props.thumbnail}
                            src={this.props.playerURL}
                        >
                            <ControlBar>
                                <ReplayControl seconds={10} order={1.1} />
                                <ForwardControl seconds={30} order={1.2} />
                                <CurrentTimeDisplay order={4.1} />
                                <TimeDivider order={4.2} />
                                <PlaybackRateMenuButton
                                  rates={[5, 2, 1, 0.5, 0.1]}
                                  order={7.1}
                                />
                                <VolumeMenuButton order={8} />
                            </ControlBar>
                        </Player>
                    
                    
                    </Modal.Body>
                    <Modal.Footer>
                            <Button onClick={this.handleClose}>
                            <Glyphicon glyph="eye-close" /> Close
                         </Button>
                    </Modal.Footer>
                </Modal>
            )
                
                
            case "Audio":
                return "";            
            default:
                return "";
          }
                
        
        
        
    }
    
    
    render(){
        console.log("Rendering player")
        console.log(this.props)
        return (
            <div className="Player">

                    {this.renderPlayer()}
            
            </div>
        )
    }
}