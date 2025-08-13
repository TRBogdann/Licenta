import { useEffect, useRef, useState } from 'react';
import applyMap from '../../tools/colormap';
import { changeTool, changeToolProps } from '../../tools/editor';
import { blendAndSave, blendPixels, changeImage, clearZoom, getImageFromCanvas, overlay } from '../../tools/myimage';
import { createBackup, deleteBackup, getItemWithId, itemExists, updateItem } from '../../tools/mylist';

function FullOverlayViewer(props) {
    const canvasTrue = useRef();
    const canvasEff = useRef();
    const [cursor, setCursor] = useState('');
    const [imgIndex, setImgIndex] = useState(1);
    const [imgBackup, setImgBackup] = useState([]);
    
    function rgbToHex(r, g, b) {
        return "#" + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
    }

    function eraseAt(ctx,x, y, size) {
        ctx.clearRect(x - size / 2, y - size / 2, size, size);
    }

    
    function decreaseIndex() {
        if (props.images.length > 1 && imgIndex > 1) {
            setImgIndex(imgIndex - 1);
        }
    }

    function increaseIndex() {
        if (props.images.length > 1 && imgIndex < props.images.length - 1) {
            setImgIndex(imgIndex + 1);
        }
    }

    useEffect(()=>
    {
        const effVector = props.backup.effects
        const setEffects = props.backup.setEffects
        deleteBackup(
            effVector,
            setEffects,
            imgIndex
        )
    },[props.edit.overlayTh])

    useEffect(() => {
        let isMounted = true;
    
        if (props.images.length > 1) {

            if(imgBackup.length < 1)
            {
                for(let i=0;i<props.images.length;i++)
                {
                    imgBackup.push('')
                }
            }
            const canvas = canvasTrue.current;
            const effects = canvasEff.current;
            const ctx = canvas?.getContext('2d');
            const ctxEff = effects?.getContext('2d')
            const img = new Image();
            let useOverlay = true;
    
            img.onload = () => {
                if (!isMounted || !canvas || !ctx) return;
                
                canvas.width = img.width;
                canvas.height = img.height;
                effects.width = img.width;
                effects.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                const img2 = new Image();

            img2.onload = () => {
                    if (!isMounted || !effects) return;
                    ctxEff.drawImage(img2, 0, 0);

                    if(useOverlay)
                {
                    
                    overlay(effects,props.edit.overlayTh*255)
                    const mapIndex = props.edit['mapIndex'];
                    
                    if (props.edit['cmaps'][mapIndex] !== 'normal') {
                        applyMap(effects, props.edit['cmaps'][mapIndex]);
                    }
                }

                };

            if(itemExists(props.backup.effects, imgIndex))
            {
                useOverlay = false
                const imgSrc = getItemWithId(props.backup.effects,imgIndex)
                img2.src = imgSrc.data
            }
            else
            {
                img2.src = props.images[imgIndex]
            }

            };
            
            const backupImg = imgBackup[imgIndex]
            const imgSrc = backupImg!==''?backupImg:props.images[0]
            console.log(imgSrc)
            img.src = imgSrc
        }
    
        return () => {
            isMounted = false;
        };
    }, [props.images, imgIndex, props.edit, imgBackup]);

    useEffect(() => {

        if(!props.tools)
            return;
    
        if (
            props.tools.currentTool.toolname !== 'pen' &&
            props.tools.currentTool.toolname !== 'erase'
        ) return;
    
        const color = props.tools.currentTool.properties?.color || "black";
        const pensize = props.tools.currentTool.properties?.pensize || 2;
        const canvas = canvasEff.current
        const ctx = canvas.getContext('2d');
        let lastPos = {x:0,y:0}
        let drawing = false;

        const handleMouseDown = props.tools.currentTool.toolname==='pen'?(e) => {
          drawing = true;
          const rect =canvas.getBoundingClientRect();
          const scaleX = canvas.width / rect.width;
          const scaleY = canvas.height / rect.height;
    
          lastPos = {
            x: Math.floor((e.clientX - rect.left) * scaleX),
            y: Math.floor((e.clientY - rect.top) * scaleY)
          };
        }:
        (e) => {
            drawing = true;
            const rect =canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
    
            const x =  Math.floor((e.clientX - rect.left) * scaleX)
            const y =  Math.floor((e.clientY - rect.top) * scaleY)
    
            ctx.strokeStyle = color;
            ctx.lineWidth = pensize;
            ctx.lineCap = "round";
            eraseAt(ctx,x,y,pensize);
          };
    
    
        const handleMouseMove = props.tools.currentTool.toolname==='pen'?(e) => {
          if (!drawing) return;
          const rect = canvas.getBoundingClientRect();
    
          const scaleX = canvas.width / rect.width;
          const scaleY = canvas.height / rect.height;
    
          const newX = Math.floor((e.clientX - rect.left) * scaleX);
          const newY = Math.floor((e.clientY - rect.top) * scaleY);
    
    
          ctx.strokeStyle = color;
          ctx.lineWidth = pensize;
          ctx.lineCap = "round";
    
          ctx.beginPath();
          ctx.moveTo(lastPos.x, lastPos.y);
          ctx.lineTo(newX, newY);
          ctx.stroke();
    
          lastPos = { x: newX, y: newY };
        }:(e) => {
            if (!drawing) return;
      
            const rect = canvas.getBoundingClientRect();
      
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
      
            const newX = Math.floor((e.clientX - rect.left) * scaleX);
            const newY = Math.floor((e.clientY - rect.top) * scaleY);
      
      
            ctx.strokeStyle = color;
            ctx.lineWidth = pensize;
            ctx.lineCap = "round";
    
            eraseAt(ctx,newX,newY,pensize)
          }
    
        const handleMouseUp = () => {
          drawing = false;
          
          const effVector = props.backup.effects;
          const setEffects = props.backup.setEffects;
          createBackup(
              effVector,
              setEffects,
              {
                  id:imgIndex,
                  data: getImageFromCanvas(canvas)
              }
          )
        };
    

        const move = (e) => handleMouseMove(e);
        const down = (e) => handleMouseDown(e);
        const up = () => handleMouseUp();
        const leave = () => handleMouseUp();
    
        canvas.addEventListener("mousedown", down);
        canvas.addEventListener("mousemove", move);
        canvas.addEventListener("mouseup", up);
        canvas.addEventListener("mouseleave", leave);
    
          // Save listeners for cleanup
        canvas._cleanupListeners = { down, move, up, leave };
        
    
        // Cleanup when tool changes
        return () => {
            if (!(!canvas || !canvas._cleanupListeners))
            {
    
            const { down, move, up, leave } = canvas._cleanupListeners;
    
            canvas.removeEventListener("mousedown", down);
            canvas.removeEventListener("mousemove", move);
            canvas.removeEventListener("mouseup", up);
            canvas.removeEventListener("mouseleave", leave);
            }
          }
      }, [props.tools]);



    useEffect(()=>
        {
            if(!props.tools)
                return;
        
            if(props.tools.currentTool.toolname !== 'colorPicker')
                return

            const effects = canvasEff.current
            const canvas = canvasTrue.current
            const ctxEff = effects.getContext('2d');
            const ctxTrue = canvas.getContext('2d');


                const handleMouseDown = (e)=>
                {
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const x = Math.floor((e.clientX - rect.left) * scaleX);
                    const y = Math.floor((e.clientY - rect.top) * scaleY);
        
                    const pixelBackground = ctxTrue.getImageData(x, y, 1, 1).data;
                    const pixelForeground = ctxEff.getImageData(x, y, 1, 1).data;
                    const pixel = blendPixels(pixelForeground,pixelBackground)
        
                    const hexColor = rgbToHex(pixel[0], pixel[1], pixel[2]);
        
                    changeTool('pen',props.tools.setCurrentTool)
                    changeToolProps({'color':hexColor},props.tools.setCurrentTool)
                    props.commandBox.setCommand('reset_color');
                }
        
                const down = (e) => handleMouseDown(e);
                effects.addEventListener("mousedown", down);
                effects._cleanupListeners = { down};
                
        
                return () => {
                    if (!(!effects || !effects._cleanupListeners))
                    {
                    const { down } = effects._cleanupListeners;
                    effects.removeEventListener("mousedown", down);
                }
                };
            
        },[props.tools])

        useEffect(() => {
            if (!props.tools || props.tools.currentTool.toolname !== 'zoom') return;
            
            const effects = canvasEff.current
            const canvas = canvasTrue.current
            const ctxEff = effects.getContext('2d');
            const ctxTrue = canvas.getContext('2d');

            let old = null;
            let zooming = false;
            let zoomStart = null;
            let zoomEnd = null;

            const handleMouseDown = (e) => {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
        
                const x = Math.floor((e.clientX - rect.left) * scaleX);
                const y = Math.floor((e.clientY - rect.top) * scaleY);
        
                old = ctxEff.getImageData(0,0,canvas.width,canvas.height)
                zoomStart = { x, y };
                zooming = true;
            };
        
            const handleMouseMove = (e) => {
                if (!zooming) return;
        
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
        
                const x = Math.floor((e.clientX - rect.left) * scaleX);
                const y = Math.floor((e.clientY - rect.top) * scaleY);
        
                ctxEff.putImageData(old,0,0);
                zoomEnd = { x, y };
        
                const start = zoomStart
        
                const w = Math.abs(x - start.x)
                const h = Math.abs(y - start.y)
                if(canvas.width<w || canvas.height<h || w<32 || h<32)
                    ctxEff.strokeStyle = 'red';
                else
                    ctxEff.strokeStyle = 'green';
        
                ctxEff.lineWidth = 1;
                ctxEff.setLineDash([4, 2]);
                ctxEff.strokeRect(
                    Math.min(start.x, x),
                    Math.min(start.y, y),
                    Math.abs(x - start.x),
                    Math.abs(y - start.y)
                );
            };
        
            const handleMouseUp = () => {
                if (!zooming) return;
        
                zooming = false;
        
                const start = zoomStart
                const end = zoomEnd
        
                if (start && end) {
                    
                    const w = Math.abs(end.x - start.x)
                    const h = Math.abs(end.y - start.y)
        
                    ctxEff.putImageData(old, 0, 0);
        
                    if(canvasEff.width<w || canvasEff.height<h || w<32 || h<32)
                        return;
        
                    const backup = props.backup
                    const ratio = effects.width/effects.height
        
                    const fg_old = old
                    const bg_old = ctxTrue.getImageData(0,0,canvas.width,canvas.height)
                    
                    const newEff = changeImage(
                        effects,
                        {'x':start.x,'y':start.y},
                        {'x':end.x,'y':end.y},
                        ratio)
        
                    const newImg = changeImage(
                        canvas,
                        {'x':start.x,'y':start.y},
                        {'x':end.x,'y':end.y},
                        ratio)  
        
                        createBackup(
                            backup.keep,
                            backup.setKeep,
                            {
                                id:imgIndex,
                                start:{'x':start.x,'y':start.y},
                                end:{'x':end.x,'y':end.y},
                                fg_img: fg_old,
                                bg_img: bg_old,
                                padding:newImg.padding
                        })
                
                    const effVector = props.backup.effects
                    const setEffects = props.backup.setEffects
                    createBackup(
                        effVector,
                        setEffects,
                        {
                            id:imgIndex,
                            data: newEff.image
                        }
                    )
            
                    updateItem(imgBackup,setImgBackup,imgIndex,newImg.image)               }
            };
        

                const down = (e) => handleMouseDown(e);
                const move = (e) => handleMouseMove(e);
                const up = () => handleMouseUp();
                const leave = () => handleMouseUp();
        
                effects.addEventListener('mousedown', down);
                effects.addEventListener('mousemove', move);
                effects.addEventListener('mouseup', up);
                effects.addEventListener('mouseleave', leave);
        
                effects._cleanupListeners = { down, move, up, leave };

        
            return () => {

                    if (!(!effects || !effects._cleanupListeners))
                { 
                    const { down, move, up, leave } = effects._cleanupListeners;
                    effects.removeEventListener('mousedown', down);
                    effects.removeEventListener('mousemove', move);
                    effects.removeEventListener('mouseup', up);
                    effects.removeEventListener('mouseleave', leave);
                }
            };
        }, [props.tools]);
        
        
        useEffect(() => {
    
            if (props.commandBox.command === 'clear') {
                    const canvas = canvasEff.current;
                    const ctx = canvas.getContext('2d')
                    if (ctx) {
                        const effVector = props.backup.effects
                        const setEffects = props.backup.setEffects
                            deleteBackup(
                                effVector,
                                setEffects,
                                imgIndex
                            )
                    }


            
                props.commandBox.setCommand('');
            }
        
            if(props.commandBox.command === 'reset_zoom')
                {
                    if(itemExists(props.backup.keep,imgIndex))
                    {
                        
                    const effects = canvasEff.current
                    const canvas = canvasTrue.current

                    const backup = getItemWithId(props.backup.keep,imgIndex)
                    
                    const foreground = clearZoom(
                        backup,
                        backup.fg_img,
                        effects
                        )
        
                    const background = clearZoom(
                        backup,
                        backup.bg_img,
                        canvas
                        )
                    
        
                    const effVector = props.backup.effects
                    const setEffects = props.backup.setEffects
                        createBackup(
                            effVector,
                            setEffects,
                            {
                                id:imgIndex,
                                data: foreground
                            }
                        )
                        updateItem(imgBackup,setImgBackup,imgIndex,background)
                    }
        
                    props.commandBox.setCommand('');
                }
        
        if (props.commandBox.command === 'save') {
            const canvas = canvasTrue.current
            const effects = canvasEff.current
            blendAndSave(effects,canvas)
            props.commandBox.setCommand('');
        }
        }, [props.commandBox]);

    return (
        <div className="image-viewer">
            <div onClick={decreaseIndex}>left</div>
            <div className='canv-container'>
                <canvas className={"canv-effects " + cursor} ref={canvasEff}></canvas>
                <canvas className="canv-true" ref={canvasTrue}></canvas>
            </div>
            <div onClick={increaseIndex}>right</div>
        </div>
    );
}

export default FullOverlayViewer;
