import { useState } from 'react';
import './mainviewer.css'
import OneImageViewer from './oneimage';
import GridViewer from './gridview';
import FullOverlayViewer from './fullovelay';


function ImageViewer(props)
{
    function getViewer(viewMode) {
        switch (viewMode) {
            case 'grid':
                return (
                    <GridViewer
                        key="grid"
                        setImages={props.setImages}
                        images={props.images}
                        edit={props.edit}
                        tools={props.tools}
                        commandBox={props.commandBox}
                        backup={props.backup}
                        ranges = {props.ranges}
                    />
                );

            case 'overlay':
                return (
                    <FullOverlayViewer
                        key="grid"
                        setImages={props.setImages}
                        images={props.images}
                        edit={props.edit}
                        tools={props.tools}
                        commandBox={props.commandBox}
                        backup={props.backup}
                        ranges = {props.ranges}
                    />
                );
            default:
                return (
                    <OneImageViewer
                        key="normal"
                        setImages={props.setImages}
                        images={props.images}
                        edit={props.edit}
                        tools={props.tools}
                        commandBox={props.commandBox}
                        backup={props.backup}
                        ranges = {props.ranges}
                    />
                );
        }
    }
    
    return (
        <>
        {getViewer(props.viewMode)}
        </>
    );
}

export default ImageViewer;