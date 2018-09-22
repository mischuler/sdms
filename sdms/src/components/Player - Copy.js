import { Modal, Image, Button, Glyphicon } from "react-bootstrap"
import React, { Component } from "react";

export default class Player extends Component {
    
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
                    <Image src={this.props.fileURL} />
                );
                break;
            
            case "Video":
                return ""
                break;
                
            case "Audio":
                return "";
                break;
            
            default:
                return "";
                break;
        }
                
        
        
        
    }
    
    
    render(){
        console.log("Rendering player")
        console.log(this.props)
        return (
            <div className="Player">
            <Modal show={this.props.show} onHide={this.handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>{this.props.Title}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {this.renderPlayer()}
                </Modal.Body>
                <Modal.Footer>
                    <a href={this.props.fileURL}><Button> <Glyphicon glyph="cloud-download" /> Download File </Button></a>
                    <Button onClick={this.handleClose}>Close</Button>
                </Modal.Footer>
            </Modal>
            
            </div>
        )
    }
}