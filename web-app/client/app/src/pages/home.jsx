import React, {useState } from "react";
import './home.css'
import Navbar from "../components/navbar/navbar";


function Home(props) {
    

    const videos = [
        "/backgrounds/bg1.mp4",
        "/backgrounds/bg2.mp4",
        "/backgrounds/bg3.mp4",
        "/backgrounds/bg4.mp4",
        "/backgrounds/bg5.mp4",
    ];

    const [videoIndex,setVideoIndex] = useState(0)

    
    function changeVideo()
    {
        if(videoIndex === videos.length-1)
        {
            setVideoIndex(0)
        }
        else
            setVideoIndex(videoIndex+1)
    }



    return (
    <div className="home-container">
        <video  
            className='vbg'
            autoPlay      
            muted
            playsInline
            src = {videos[videoIndex]}
            onEnded={changeVideo}
        >
        </video>
        
        <div className="home-filter">
        </div>

        <div className="abs-container">
        <Navbar setColor = {props.setColor} image = {props.image}>

        </Navbar>

        <div className="home-text">
        <div className="home-title">Medical image analysis tools</div>
        <div className="home-desc">Image analysis solutions designed to assist healthcare professionals in accurate diagnosis and medical image segmentation. </div>
        
        <div className="home-buttons">
        <button className="btn-template-light">Collab</button>
        <button className="btn-template-dark">Press me too</button>
        </div>
        </div>
        </div>

    </div>
    );
}

export default Home;
