import { useEffect, useState } from "react";
import EditorBar from "./components/old_editorbar/maineditor";
import ImageViewer from "./components/old_viewer/mainviewer";
import './Test.css'

function Test()
{
    const [image, setImage] = useState(null);
    const [classes,setClasses] = useState([]);
    const [probs,setProbs] = useState([]);
    const [images,setImages] = useState([]);
    const [cmapIndex,setCmapIndex] = useState(0);
    const [currentTool,setCurrentTool] = useState({toolname:'select',properties:{}});
    const [command,setCommand] = useState('')
    const [keep,setKeep]=useState([])
    const [effects,setEffects]=useState([])
    const [viewMode,setViewMode] = useState('normal')
    const [ranges,setRanges] = useState([])
    const [correction,setCorrection] = useState({run:null})
    const [overlayTh,setOverlayTh] = useState(0.5)

    const dummyEvent = 
    {
      preventDefault:()=>{}
    };

    useEffect(()=>
    {
      if(command==='grid-view')
      {
        setViewMode('grid')
        setCommand('');
      }

      if(command==='full-overlay-view')
      {
          setViewMode('overlay')
          setCommand('');
      }

      if(command==='normal-view')
      {
        setViewMode('normal')
        setCommand('');
      }
      if(command==='get-activations')
      {
        handleActivations(dummyEvent);
        setCommand('');
      }
      if(command==='get-masks')
      {
        handleSubmit(dummyEvent);
        setCommand('');
      }

      if(command==='th-up')
      {
        if(overlayTh<1)
        {
          setOverlayTh(overlayTh+0.1)
        }
        setCommand('');
      }

      if(command==='th-down')
        {
          if(overlayTh>0)
          {
            setOverlayTh(overlayTh-0.1)
          }
          setCommand('');
        }
      
    },[command])

  

    const cmaps = ['normal', 'viridis', 'plasma', 'inferno', 'magma', 'jet', 'hot', 'cool']

    const handleSubmit = async (e) => {
        e.preventDefault();
        if(!image)
            return
        const formData = new FormData();
        formData.append('image', image); 
        try {
            const response = await fetch('http://localhost:5000/all', {
              method: 'POST',
              body: formData
            });
            const data = await response.json();
            const roundedArray = data['probs'].map(num => Math.round(num * 100) / 100)
            setKeep([])
            setEffects([])
            setProbs(roundedArray)
            setClasses(data['classes'])
            const reader = new FileReader();
            reader.onload = function(event) {
              const newImages = [event.target.result,data['mask1'],data['mask2'],data['mean'],data['smooth']];
              const newRanges = [{a:0,b:255},{a:0,b:255},{a:0,b:255},{a:0,b:255},{a:0,b:255}]
              setRanges(newRanges)
              setImages(newImages);
              
            };
            reader.readAsDataURL(image);
            

          } catch (error) {
            console.error('Error uploading image:', error);
          }
    }

    const handleActivations = async (e) => {
      e.preventDefault();
      if(!image)
          return
      const formData = new FormData();
      formData.append('image', image); 
      try {
          const response = await fetch('http://localhost:5000/all_activ', {
            method: 'POST',
            body: formData
          });
          const data = await response.json();
          const roundedArray = data['probs'].map(num => Math.round(num * 100) / 100)
          setKeep([])
          setEffects([])
          setProbs(roundedArray)
          setClasses(data['classes'])
          const reader = new FileReader();
          reader.onload = function(event) {
            const newImages = [event.target.result]
            const newRanges = [{a:0,b:255}]
            for(let i=1; i<data['size']+1; i++)
            {
              newImages.push(data['img_'+i])
              newRanges.push(data['range_'+i])
            }
            setRanges(newRanges)
            setImages(newImages);
          };
          reader.readAsDataURL(image);
          

        } catch (error) {
          console.error('Error uploading image:', error);
        }
  }


    return (
      <div>
    <form onSubmit={handleSubmit}>
      <input type="file" accept="image/*" onChange={(e) => 
    {
      setImage(e.target.files[0]);
    }} />
      <button type="submit">Upload</button>
    </form>
    <div className="edit-image-container">
    <ImageViewer viewMode={viewMode} setImages={setImages} images = {images} edit={{"cmaps":cmaps,"mapIndex":cmapIndex,"setMapIndex":setCmapIndex,'correction':correction,'setCorrection':setCorrection,'overlayTh':overlayTh,'setOverlayTh':setOverlayTh}} tools={{'currentTool':currentTool,'setCurrentTool':setCurrentTool}} commandBox={{command,setCommand}} backup={{keep,setKeep,effects,setEffects}} ranges={ranges}></ImageViewer>
    <EditorBar viewMode={viewMode} classes={classes} probs={probs} edit={{"cmaps":cmaps,"mapIndex":cmapIndex,"setMapIndex":setCmapIndex,'correction':correction,'setCorrection':setCorrection,'overlayTh':overlayTh,'setOverlayTh':setOverlayTh}} tools={{'currentTool':currentTool,'setCurrentTool':setCurrentTool}} commandBox={{command,setCommand}} backup={{keep,setKeep,effects,setEffects}}></EditorBar>
    </div>
    </div>
    );
}

export default Test;