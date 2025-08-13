import './App.css';
import Home from './pages/home';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import Tools from './pages/tools';
import { useEffect, useState } from 'react';
// import Test from './Test';
import Loader from './pages/load';
import Editor from './pages/editor';
import LogSign from './pages/logsign';

function App() {

  const colormaps = [
      ["rgb(68, 1, 84)", "rgb(59, 82, 139)", "rgb(33, 145, 140)", "rgb(94, 201, 98)", "rgb(183, 222, 48)", "rgb(253, 231, 37)", "rgba(33, 145, 140, 0.3)", "rgba(183, 222, 48, 0.3)"],
      ["rgb(13, 8, 135)", "rgb(75, 3, 161)", "rgb(133, 21, 158)", "rgb(185, 55, 123)", "rgb(229, 101, 71)", "rgb(249, 253, 56)", "rgba(133, 21, 158, 0.3)", "rgba(229, 101, 71, 0.3)"],
      ["rgb(0, 0, 4)", "rgb(50, 5, 35)", "rgb(120, 18, 58)", "rgb(191, 54, 43)", "rgb(249, 142, 8)", "rgb(252, 255, 164)", "rgba(120, 18, 58, 0.3)", "rgba(249, 142, 8, 0.3)"],
      ["rgb(0, 0, 3)", "rgb(41, 10, 62)", "rgb(101, 20, 101)", "rgb(162, 51, 94)", "rgb(222, 119, 73)", "rgb(252, 253, 191)", "rgba(101, 20, 101, 0.3)", "rgba(222, 119, 73, 0.3)"],
      ["rgb(0, 32, 77)", "rgb(0, 74, 135)", "rgb(63, 111, 135)", "rgb(131, 148, 121)", "rgb(197, 189, 97)", "rgb(255, 233, 69)", "rgba(63, 111, 135, 0.3)", "rgba(197, 189, 97, 0.3)"],
      ["rgb(11, 0, 0)", "rgb(132, 0, 0)", "rgb(255, 78, 0)", "rgb(255, 190, 0)", "rgb(255, 255, 144)", "rgb(255, 255, 255)", "rgba(255, 78, 0, 0.3)", "rgba(255, 255, 144, 0.3)"],
      ["rgb(0, 255, 255)", "rgb(51, 204, 255)", "rgb(102, 153, 255)", "rgb(153, 102, 255)", "rgb(204, 51, 255)", "rgb(255, 0, 255)", "rgba(102, 153, 255, 0.3)", "rgba(204, 51, 255, 0.3)"],
      ["rgb(0, 0, 0)", "rgb(51, 51, 51)", "rgb(102, 102, 102)", "rgb(153, 153, 153)", "rgb(204, 204, 204)", "rgb(255, 255, 255)", "rgba(102, 102, 102, 0.3)", "rgba(204, 204, 204, 0.3)"]
  ];



  const [colorIndex,setColorIndex] = useState(7);
  const [imagePath,setImagePath] = useState('/logos/dna_custom/d4.gif')
  const [serverRoute,setServerRoute] = useState({'mask':'','activation':'','type':''});
  const [images,setImages] = useState([])
  const [effects,setEffects] = useState([])
  const [imageType,setImageType] = useState('2d');
  const [fileCount,setFileCount] = useState(1);
  const [ranges,setRanges] = useState([]);
  const [imgBackup,setImgBackup] = useState([]);
  const [probs,setProbs] = useState([]);
  const [labels,setLabels] = useState([]); 
  const [file,setFile] = useState('');
  const [shape,setShape] = useState([]);
  const [ctscans,setCtscans] = useState([]);
  const [axis,setAxis] = useState(0);
  const [ctmask,setCtmask] = useState([]);
  const [slice,setSlice] = useState(0);

  useEffect(()=>
  {
    console.log(ctscans);
  },[ctscans])

  useEffect(()=>
  {
    console.log(ctmask);
  },[ctmask])
  const data = {
    settings:{imageType,setImageType,fileCount,setFileCount},
    content:{file,setFile,images,setImages,effects,setEffects,ranges,setRanges,imgBackup,setImgBackup},
    contentMri:{slice,setSlice,shape,setShape,axis,setAxis,ctmask,setCtmask,ctscans,setCtscans},
    result:{probs,setProbs,labels,setLabels},
    routes:serverRoute
  };

  useEffect(()=>
  {
    const logo_files = [
      '/logos/dna_custom/d2.gif',
      '/logos/dna_custom/d3.gif',
      '/logos/dna_custom/d8.gif',
      '/logos/dna_custom/d4.gif',
      '/logos/dna_custom/d5.gif',
      '/logos/dna_custom/d6.gif',
      '/logos/dna_custom/d7.gif',
      '/logos/dna_custom/d8.gif'
    ]

    setImagePath(logo_files[colorIndex])
  },[colorIndex])


  //To Do
  // const package = null;

  function changeTheme()
  {
      if(colorIndex === colormaps.length-1)
      {
          setColorIndex(0)
      }
      else
          setColorIndex(colorIndex+1)

      const palette = colormaps[colorIndex]

      for(let i=0;i<6;i+=1)
      {
          document.documentElement.style.setProperty(`--c${i+1}`, palette[i]);
      }
      document.documentElement.style.setProperty(`--t1`, palette[6]);
      document.documentElement.style.setProperty(`--t2`, palette[7]);
  }

  return (
    <div className='content'>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home setColor = {changeTheme} image = {imagePath} />} />
        <Route path='/tools' element={<Tools image = {imagePath} setServerRoute={setServerRoute} settings={{imageType,setImageType,fileCount,setFileCount}}/>}/>
        <Route path= '/load' element={<Loader data={data}/>}></Route>
        {/* <Route path= '/test' element={<Test/>}></Route> */}
        <Route path= '/editor' element={<Editor data={data}/>}></Route>
        <Route path='/logsign' element={<LogSign data={data}></LogSign>}></Route>
      </Routes>
    </BrowserRouter>
    </div>
  );
}

export default App;
