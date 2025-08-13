import React, { useEffect, useRef } from 'react';
import Dropzone from 'dropzone';
import "dropzone/dist/dropzone.css";
import { useNavigate } from 'react-router-dom';
import pako from 'pako'
import * as nifti from "nifti-reader-js";
import { getMaskFromNii, getSliceFromNii } from '../tools/myimage';

Dropzone.autoDiscover = false;

function getTypedArray(datatypeCode, buffer) {
  switch (datatypeCode) {
    case 2:    // DT_UINT8
      return new Uint8Array(buffer);
    case 4:    // DT_INT16
      return new Int16Array(buffer);
    case 8:    // DT_INT32
      return new Int32Array(buffer);
    case 16:   // DT_FLOAT32
      return new Float32Array(buffer);
    case 32:   // DT_COMPLEX64 (2 x Float32)
      return new Float32Array(buffer); // you must interpret pairs as real + imag
    case 64:   // DT_FLOAT64
      return new Float64Array(buffer);
    case 128:  // DT_RGB24 (3 x uint8 per voxel)
      return new Uint8Array(buffer); // interpret every 3 bytes as RGB
    case 256:  // DT_INT8
      return new Int8Array(buffer);
    case 512:  // DT_UINT16
      return new Uint16Array(buffer);
    case 768:  // DT_UINT32
      return new Uint32Array(buffer);
    case 1536: // DT_FLOAT128
      throw new Error("DT_FLOAT128 (128-bit float) is not supported in JS");
    case 1792: // DT_COMPLEX128 (2 x Float64)
      return new Float64Array(buffer); // interpret pairs as complex numbers
    case 2048: // DT_COMPLEX256 (2 x Float128)
      throw new Error("DT_COMPLEX256 (256-bit complex) not supported in JS");
    case 2304: // DT_RGBA32 (4 x uint8 per voxel)
      return new Uint8Array(buffer); // interpret every 4 bytes as RGBA
    case 1:    // DT_BINARY
      // 1-bit per voxel, no TypedArray support — must manually extract bits
      return null;
    default:
      throw new Error(`Unsupported NIfTI datatypeCode: ${datatypeCode}`);
  }
}


function Loader(props) {

  const dropzoneRef = useRef(null);
  const navigate = useNavigate();

    const settings = props.data.settings;
    const content = props.data.content;
    const routes = props.data.routes;
    const result = props.data.result;

  useEffect(() => {
    let serverUrl = routes.activation
    if(routes.mask!=='')
    {
        serverUrl = routes.mask
    }
    if(serverUrl==='')
    {
        navigate('/tools',{replace:true});
        return;
    }


  const loadNii = (buffer) => {
    if (nifti.isNIFTI(buffer)) {
      const header = nifti.readHeader(buffer);
      const tempData = nifti.readImage(header, buffer);
      
      console.log(header.datatypeCode)
      const data = getTypedArray(header.datatypeCode,tempData)

      let minVal = data[0]
      let maxVal = data[0]

      for(let i=1;i<data.length;i++)
      {
        if(data[i]<minVal)
        {
          minVal = data[i]
        }
        if(data[i]>maxVal)
        {
          maxVal = data[i]
        }
      }

      console.log(minVal)
      console.log(maxVal)

      for(let i=0;i<data.length;i++)
        {
          data[i] = Math.round(((data[i]-minVal)/(maxVal-minVal))*255)
        }
      console.log(header)
      return data
    }
  };



    const dz = routes.type!=='nii'?new Dropzone(dropzoneRef.current, {
      url: serverUrl,
      maxFiles: 5,
      acceptedFiles: "image/*",
      addRemoveLinks: true,
      paramName: 'image'
    }): new Dropzone(dropzoneRef.current, {
      autoDiscover: false,
      url: serverUrl,           
      autoProcessQueue: false,     
      uploadMultiple: true,        
      parallelUploads: 10,          
      maxFiles: 10,                 
      acceptedFiles: ".nii",       
      addRemoveLinks: true,
      maxFilesize: 300,
      paramName: "images",
      init: function() {
        const dz = this;
        
        let uploadTriggered = false;
        dz.on("addedfile", function(file) {
          if (dz.files.length === 4 && !uploadTriggered) {
            uploadTriggered = true;
            setTimeout(() => {
              dz.processQueue();
            }, 100); 
          }
        });
    
        dz.on("sendingmultiple", function(data, xhr, formData) {
          // Append additional data if needed
          console.log("Sending all 4 files");
        });
    
        dz.on("successmultiple", async function(files, response) {
          const compressed = Uint8Array.from(atob(response['data']), c => c.charCodeAt(0));
          const decompressed = pako.inflate(compressed);
          const imgArray = [];

          for(let i=0;i<4;i++)
          {
          const file = files[i];
          
          if (!file) continue;

          const arrayBuffer = await file.arrayBuffer();
          let current = null;
          if (nifti.isCompressed(arrayBuffer)) {
            const decompressed = nifti.decompress(arrayBuffer);
            current = loadNii(decompressed);
          } else {
            current = loadNii(arrayBuffer);
          }
          imgArray.push(current);
          }

          console.log(response['shape'])
          const newImages =[
            getSliceFromNii(100,0,imgArray[1],response['shape']),
            getMaskFromNii(100,0,decompressed,response['shape'])
          ]

          settings.setImageType('3d');
          props.data.contentMri.setShape(response['shape'])
          props.data.contentMri.setCtscans(imgArray);
          props.data.contentMri.setCtmask(decompressed);
          content.setImgBackup([])
          content.setEffects([])
          result.setProbs([])
          result.setLabels([])

          content.setImages(newImages)
          content.setRanges([{a:0,b:255},{a:0,b:255}])
          navigate('/editor',{replace:true})

        });
    
        dz.on("error", function(file, errorMessage) {
          console.error("Error uploading:", errorMessage);
        });
      }
    });


  
    dz.on("success", (file, response) => {
      if(routes.type!=='nii'){
        const roundedArray = response['probs'].map(num => Math.round(num * 100) / 100)
        content.setImgBackup([])
        content.setEffects([])
        result.setProbs(roundedArray)
        result.setLabels(response['classes'])
        const reader = new FileReader();
        reader.onload = function(event) {
          const newImages = [event.target.result];
          const newRanges = [{a:0,b:255}];
          for(let i=1; i<response['size']+1; i++)
          {
            newImages.push(response['img_'+i])
            newRanges.push({a:0,b:255})
          }
          content.setImages(newImages)
          content.setRanges(newRanges)

          navigate('/editor',{replace:true})
        };
        content.setFile(file)
        reader.readAsDataURL(file);}
    });

    return () => dz.destroy();
  }, []);

  return (
    <form ref={dropzoneRef} className="dropzone" style={{ border: '2px dashed #888', padding: 20 }} />
  );
}

export default Loader;
