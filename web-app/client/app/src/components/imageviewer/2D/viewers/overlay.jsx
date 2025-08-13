import { useEffect, useRef, useState } from "react";
import { createBackup, deleteBackup, getItemWithId, itemExists, updateItem } from "../../../../tools/mylist";
import { applyCorrection, blendAndSave, blendPixels, changeImage, clearZoom, eraseAt, getImageFromCanvas, overlay, rgbToHex } from "../../../../tools/myimage";
import applyMap from "../../../../tools/colormap";

function OverlayView(props)
{
    const settings = props.data.settings;
    const content = props.data.content;
    const tool = props.data.tool;
    const palette = props.data.palette;
    const commandBox = props.data.commandBox;

    const canvasTrue = useRef(null);
    const canvasEff = useRef(null);
    const [imgIndex, setImgIndex] = useState(1);
    const [imgBackup, setImgBackup] = useState([]);


    function decreaseIndex() {
        if (imgIndex > 1) {
            setImgIndex(imgIndex - 1);
        }
    }

    function increaseIndex() {
        if (imgIndex < content.images.length - 1) {
            setImgIndex(imgIndex + 1);
        }
    }

    useEffect(()=>
        {

            deleteBackup(
                content.effects,
                content.setEffects,
                imgIndex
            )
        },[settings.overlay])
    
        useEffect(() => {
            let isMounted = true;
        
            if (content.images.length > 1) {
    
                if(imgBackup.length < 1)
                {
                    for(let i=0;i<content.images.length;i++)
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
                        
                        let th = settings.imageType==='3d'?0:settings.overlay
                        overlay(effects,th*255)
                        
                        if (palette.cmap!=='normal') {
                            applyMap(effects, palette.cmap);
                        }

                        if(palette.correction!=='none')
                        {
                            applyCorrection(effects,content.ranges[imgIndex].a,content.ranges[imgIndex].b,palette.correction);
                        }
                    }
    
                    };
    
                if(itemExists(content.effects, imgIndex))
                {
                    useOverlay = false
                    const imgSrc = getItemWithId(content.effects,imgIndex)
                    img2.src = imgSrc.data
                }
                else
                {
                    img2.src = content.images[imgIndex]
                }
    
                };
                
                const backupImg = imgBackup[imgIndex]
                const imgSrc = backupImg!==''?backupImg:content.images[0]
                console.log(imgSrc)
                img.src = imgSrc
            }
        
            return () => {
                isMounted = false;
            };
        }, [content.images, imgIndex, palette, imgBackup]);
    
        useEffect(() => {
    

            if (
                tool.toolName !== 'pen' &&
                tool.toolName !== 'erase'
            ) return;
        
            const color = tool.color
            const pensize = tool.pensize
            const canvas = canvasEff.current
            const ctx = canvas.getContext('2d');
            let lastPos = {x:0,y:0}
            let drawing = false;
    
            const handleMouseDown = tool.toolName==='pen'?(e) => {
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
        
        
            const handleMouseMove = tool.toolName==='pen'?(e) => {
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
              
              createBackup(
                  content.effects,
                  content.setEffects,
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
          }, [tool]);
    
    
    
        useEffect(()=>
            {
                if(tool.toolName !== 'colorPicker')
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
            
                        tool.setColor(hexColor);
                        tool.setToolName('pen');
                        
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
                
            },[tool.toolName])
    
            useEffect(() => {
                if (tool.toolName !== 'zoom') return;
                
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
                        
                        if(itemExists(props.backup.keep,imgIndex))
                        {
                            return;
                        }

                        if(canvasEff.width<w || canvasEff.height<h || w<32 || h<32)
                            return;
            
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
                                content.imgBackup,
                                content.setImgBackup,
                                {
                                    id:imgIndex,
                                    start:{'x':start.x,'y':start.y},
                                    end:{'x':end.x,'y':end.y},
                                    fg_img: fg_old,
                                    bg_img: bg_old,
                                    padding:newImg.padding
                            })
                    
                        createBackup(
                            content.effects,
                            content.setEffects,
                            {
                                id:imgIndex,
                                data: newEff.image
                            }
                        )
                        
                        updateItem(imgBackup,setImgBackup,imgIndex,newImg.image)               }
                        tool.setToolName('select');
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
            }, [tool.toolName]);
            
            
            useEffect(() => {
        
                if (commandBox.command === 'clear') {
                        const canvas = canvasEff.current;
                        const ctx = canvas.getContext('2d')
                        if (ctx) {
                                deleteBackup(
                                    content.effects,
                                    content.setEffects,
                                    imgIndex
                                )
                        }
    
                        commandBox.setCommand('');
                }
            
                if(commandBox.command === 'clear-zoom')
                    {
                        if(itemExists(content.imgBackup,imgIndex))
                        {
                            
                        const effects = canvasEff.current
                        const canvas = canvasTrue.current
    
                        const backup = getItemWithId(content.imgBackup,imgIndex)
                        
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
                        
            
                            createBackup(
                                content.canvasTrue,
                                content.setEffects,
                                {
                                    id:imgIndex,
                                    data: foreground
                                }
                            )
                            updateItem(imgBackup,setImgBackup,imgIndex,background)
                        }
            
                        commandBox.setCommand('');
                    }
            
            if (commandBox.command === 'save') {
                const canvas = canvasTrue.current
                const effects = canvasEff.current
                blendAndSave(effects,canvas)
                commandBox.setCommand('');
            }
            }, [commandBox]);
    
        return (
            <div className="image-viewer">
            <div class="btn-template-triangle-container left-orientation">
                <div class="btn-template-triangle"
                onClick={decreaseIndex}></div>
            </div>
                <div className='canv-container'>
                    <canvas className={"canv-effects " + settings.cursor} ref={canvasEff}></canvas>
                    <canvas className="canv-true" ref={canvasTrue}></canvas>
                </div>
                <div class="btn-template-triangle-container right-orientation">
                <div class="btn-template-triangle"
                onClick={increaseIndex}></div>
            </div>
            </div>
        );
}

export default OverlayView;