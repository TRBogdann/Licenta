import { useEffect, useRef, useState } from "react";
import { applyCorrection, blendAndSave, blendPixels, changeImage, clearZoom, eraseAt, getImageFromCanvas, rgbToHex } from "../../../../tools/myimage";
import { createBackup, deleteBackup, getItemWithId, itemExists, updateItem } from "../../../../tools/mylist";
import applyMap from "../../../../tools/colormap";

function GridView(props)
{

    const settings = props.data.settings;
    const content = props.data.content;
    const tool = props.data.tool;
    const palette = props.data.palette;
    const commandBox = props.data.commandBox;

    const copy = useRef([])
    const canvasRefs = useRef([]);
    const canvasEffRefs = useRef([]);
    const drawing = useRef([]); 
    const lastPos = useRef([]);
    const old = useRef([])
    const zoomStart = useRef([]);
    const zoomEnd = useRef([]);
    const zooming = useRef([])
    const [selected,setSelected] = useState(0);
  
    useEffect(()=>
    {
        if(content.images.length>0)
        {
          console.log(content.imgBackup);

            canvasRefs.current.length = content.images.length;
            canvasEffRefs.current.length = content.images.length;
        
            for (let i = 0; i < canvasEffRefs.current.length; i++) {
              const canvasTrue = canvasRefs.current[i];
              const canvasEff = canvasEffRefs.current[i];
              const ctxTrue = canvasTrue.getContext("2d");
              const ctxEff = canvasEff.getContext("2d");
              
              const img = new Image();
              img.onload = ()=>
              {
                canvasTrue.width = img.width;
                canvasTrue.height = img.height;
                canvasEff.width = img.width;
                canvasEff.height = img.height;

                if(itemExists(content.effects,i))
                  {
                      const backup = getItemWithId(content.effects,i); 
                      const img2 = new Image();
                      img2.onload=()=>
                      {
                          ctxEff.drawImage(img2,0,0);
                      }
                      img2.src = backup.data;
                  }
                  else{
                      ctxEff.clearRect(0,0,img.width,img.height);
                  }
      
                  ctxTrue.drawImage(img,0,0);
                  copy.current[i] = ctxTrue.getImageData(0,0,img.width,img.height);
      
                  if(palette.cmap!=='normal')
                  {
                      applyMap(canvasTrue,palette.cmap);
                  }
                  if(palette.correction!=='none')
                  {
                      applyCorrection(canvasTrue,content.ranges[i].a,content.ranges[i].b,palette.correction)
                  }
              }
              img.src = content.images[i];
            }
        }
    },[content.images,palette])
  
    function isSelected(index)
    {
      if(index===selected)
          return 'selected-box';

      return '';
    }

    useEffect(()=>
      {
      
          if(tool.toolName !== 'select')
              return;
          
              const handleMouseDown = (e,index) =>
              {
                  setSelected(index);
              }
      
              for (let i = 0; i < canvasEffRefs.current.length; i++) {
                  const canvas = canvasEffRefs.current[i];
                  if (!canvas) continue;
            
                  const down = (e) => handleMouseDown(e, i);
                  canvas.addEventListener("mousedown", down);
                  canvas._cleanupListeners = { down};
                }
      
              return () => {
              for (let i = 0; i < canvasEffRefs.current.length; i++) {
                  const canvas = canvasEffRefs.current[i];
                  if (!canvas || !canvas._cleanupListeners) continue;
                  const { down } = canvas._cleanupListeners;
                  canvas.removeEventListener("mousedown", down);
              }
              };
      },[tool.toolName])

      useEffect(()=>
        {
            if(tool.toolName !== 'colorPicker')
                return;
        
                const handleMouseDown = (e,index)=>
                {
                    const canvasEff = canvasEffRefs.current[index]
                    const canvasTrue = canvasRefs.current[index]
                    const ctxEff = canvasEff.getContext('2d');
                    const ctxTrue = canvasTrue.getContext('2d');
        
                    const rect = canvasEff.getBoundingClientRect();
                    const scaleX = canvasEff.width / rect.width;
                    const scaleY = canvasEff.height / rect.height;
                    const x = Math.floor((e.clientX - rect.left) * scaleX);
                    const y = Math.floor((e.clientY - rect.top) * scaleY);
        
                    const pixelBackground = ctxTrue.getImageData(x, y, 1, 1).data;
                    const pixelForeground = ctxEff.getImageData(x, y, 1, 1).data;
                    const pixel = blendPixels(pixelForeground,pixelBackground)
        
                    const hexColor = rgbToHex(pixel[0], pixel[1], pixel[2]);
        
                    tool.setColor(hexColor);
                    tool.setToolName('pen');
                    
                }
        
                for (let i = 0; i < canvasEffRefs.current.length; i++) {
                    const canvas = canvasEffRefs.current[i];
                    if (!canvas) continue;
              
                    const down = (e) => handleMouseDown(e, i);
                    canvas.addEventListener("mousedown", down);
                    canvas._cleanupListeners = { down};
                  }
        
                return () => {
                for (let i = 0; i < canvasEffRefs.current.length; i++) {
                    const canvas = canvasEffRefs.current[i];
                    if (!canvas || !canvas._cleanupListeners) continue;
                    const { down } = canvas._cleanupListeners;
                    canvas.removeEventListener("mousedown", down);
                }
                };
            
        },[tool.toolName])

useEffect(() => {
          if (
              tool.toolName !== 'pen' &&
              tool.toolName !== 'erase'
          ) return;
      
          const color = tool.color
          const pensize = tool.pensize
      
          const handleMouseDown = tool.toolName==='pen'?(e, index) => {
            drawing.current[index] = true;
            const canvas = canvasEffRefs.current[index]
            const rect =canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
      
            lastPos.current[index] = {
              x: Math.floor((e.clientX - rect.left) * scaleX),
              y: Math.floor((e.clientY - rect.top) * scaleY)
            };
          }:
          (e, index) => {
              drawing.current[index] = true;
              const canvas = canvasEffRefs.current[index]
              const rect =canvas.getBoundingClientRect();
              const scaleX = canvas.width / rect.width;
              const scaleY = canvas.height / rect.height;
      
              const x =  Math.floor((e.clientX - rect.left) * scaleX)
              const y =  Math.floor((e.clientY - rect.top) * scaleY)
      
              eraseAt(canvas.getContext('2d'),x,y,pensize);
            };
      
      
          const handleMouseMove = tool.toolName==='pen'?(e, index) => {
            if (!drawing.current[index]) return;
      
            const canvas = canvasEffRefs.current[index];
            const ctx = canvas.getContext("2d");
            const rect = canvas.getBoundingClientRect();
      
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
      
            const newX = Math.floor((e.clientX - rect.left) * scaleX);
            const newY = Math.floor((e.clientY - rect.top) * scaleY);
      
      
            ctx.strokeStyle = color;
            ctx.lineWidth = pensize;
            ctx.lineCap = "round";
      
            ctx.beginPath();
            ctx.moveTo(lastPos.current[index].x, lastPos.current[index].y);
            ctx.lineTo(newX, newY);
            ctx.stroke();
      
            lastPos.current[index] = { x: newX, y: newY };
          }:(e, index) => {
              if (!drawing.current[index]) return;
        
              const canvas = canvasEffRefs.current[index];
              const ctx = canvas.getContext("2d");
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
      
          const handleMouseUp = (index) => {
            drawing.current[index] = false;
            createBackup(
                content.effects,
                content.setEffects,
                {
                    id:index,
                    data: getImageFromCanvas(canvasEffRefs.current[index])
                }
            )
          };
      
          for (let i = 0; i < canvasEffRefs.current.length; i++) {
            const canvas = canvasEffRefs.current[i];
            if (!canvas) continue;
      
            const move = (e) => handleMouseMove(e, i);
            const down = (e) => handleMouseDown(e, i);
            const up = () => handleMouseUp(i);
            const leave = () => handleMouseUp(i);
      
            canvas.addEventListener("mousedown", down);
            canvas.addEventListener("mousemove", move);
            canvas.addEventListener("mouseup", up);
            canvas.addEventListener("mouseleave", leave);
      
            // Save listeners for cleanup
            canvas._cleanupListeners = { down, move, up, leave };
          }
      
          // Cleanup when tool changes
          return () => {
            for (let i = 0; i < canvasEffRefs.current.length; i++) {
              const canvas = canvasEffRefs.current[i];
              if (!canvas || !canvas._cleanupListeners) continue;
      
              const { down, move, up, leave } = canvas._cleanupListeners;
      
              canvas.removeEventListener("mousedown", down);
              canvas.removeEventListener("mousemove", move);
              canvas.removeEventListener("mouseup", up);
              canvas.removeEventListener("mouseleave", leave);
            }
          };
        }, [tool]);


        useEffect(() => {
          if (tool.toolName !== 'zoom') return;
      
          const handleMouseDown = (e, index) => {
              const canvas = canvasEffRefs.current[index];
              const ctx = canvas.getContext('2d')
              const rect = canvas.getBoundingClientRect();
              const scaleX = canvas.width / rect.width;
              const scaleY = canvas.height / rect.height;
      
              const x = Math.floor((e.clientX - rect.left) * scaleX);
              const y = Math.floor((e.clientY - rect.top) * scaleY);
      
              old.current[index] = ctx.getImageData(0,0,canvas.width,canvas.height)
              zoomStart.current[index] = { x, y };
              zooming.current[index] = true;
          };
      
          const handleMouseMove = (e, index) => {
              if (!zooming.current[index]) return;
      
              const canvas = canvasEffRefs.current[index];
              const ctx = canvas.getContext('2d');
              const rect = canvas.getBoundingClientRect();
              const scaleX = canvas.width / rect.width;
              const scaleY = canvas.height / rect.height;
      
              const x = Math.floor((e.clientX - rect.left) * scaleX);
              const y = Math.floor((e.clientY - rect.top) * scaleY);
      
              ctx.putImageData(old.current[index],0,0);
              zoomEnd.current[index] = { x, y };
      
              const start = zoomStart.current[index];
      
              const w = Math.abs(x - start.x)
              const h = Math.abs(y - start.y)
              if(canvas.width<w || canvas.height<h || w<32 || h<32)
                  ctx.strokeStyle = 'red';
              else
                  ctx.strokeStyle = 'green';
      
              ctx.lineWidth = 1;
              ctx.setLineDash([4, 2]);
              ctx.strokeRect(
                  Math.min(start.x, x),
                  Math.min(start.y, y),
                  Math.abs(x - start.x),
                  Math.abs(y - start.y)
              );
          };
      
          const handleMouseUp = (index) => {
              if (!zooming.current[index]) return;

              zooming.current[index] = false;
      
              const canvasFg = canvasEffRefs.current[index];
              const ctxFg = canvasFg.getContext('2d');
              const canvasBg = canvasRefs.current[index];
              const ctxBg = canvasBg.getContext('2d');
              const start = zoomStart.current[index];
              const end = zoomEnd.current[index];

              
            
            if(itemExists(content.imgBackup,index))
            {
                
                  ctxFg.putImageData(old.current[index], 0, 0);
                  return;
            }
      
              if (start && end) {
                  
                  const w = Math.abs(end.x - start.x)
                  const h = Math.abs(end.y - start.y)
      
                  ctxFg.putImageData(old.current[index], 0, 0);
                  
                  if(canvasFg.width<w || canvasFg.height<h || w<32 || h<32)
                      return;
      
                  ctxBg.putImageData(copy.current[index],0,0);
                  const ratio = canvasFg.width/canvasFg.height
                  const fg_old = old.current[index]
                  const bg_old = ctxBg.getImageData(0,0,canvasBg.width,canvasBg.height)
                  
                  const newEff = changeImage(
                      canvasFg,
                      {'x':start.x,'y':start.y},
                      {'x':end.x,'y':end.y},
                      ratio)
      
                  const newImg = changeImage(
                      canvasBg,
                      {'x':start.x,'y':start.y},
                      {'x':end.x,'y':end.y},
                      ratio)  
      
                      createBackup(
                        content.imgBackup,
                        content.setImgBackup,
                        {
                            id:index,
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
                              id:index,
                              data: newEff.image
                          }
                      )
                      updateItem(content.images,content.setImages,index,newImg.image)
                      tool.setToolName('select');
                    }
          };
      
          for (let i = 0; i < canvasEffRefs.current.length; i++) {
              const canvas = canvasEffRefs.current[i];
              if (!canvas) continue;
      
              const down = (e) => handleMouseDown(e, i);
              const move = (e) => handleMouseMove(e, i);
              const up = () => handleMouseUp(i);
              const leave = () => handleMouseUp(i);
      
              canvas.addEventListener('mousedown', down);
              canvas.addEventListener('mousemove', move);
              canvas.addEventListener('mouseup', up);
              canvas.addEventListener('mouseleave', leave);
      
              canvas._cleanupListeners = { down, move, up, leave };
          }
      
          return () => {
              for (let i = 0; i < canvasEffRefs.current.length; i++) {
                  const canvas = canvasEffRefs.current[i];
                  if (!canvas || !canvas._cleanupListeners) continue;
                  const { down, move, up, leave } = canvas._cleanupListeners;
                  canvas.removeEventListener('mousedown', down);
                  canvas.removeEventListener('mousemove', move);
                  canvas.removeEventListener('mouseup', up);
                  canvas.removeEventListener('mouseleave', leave);
              }
          };
      }, [tool.toolName]);

      useEffect(() => {
    
        if (commandBox.command === 'clear') {
                const canvas = canvasEffRefs.current[selected];
                const ctx = canvas.getContext('2d')
                if (ctx) {
                    ctx.clearRect(0,0,canvas.width,canvas.height);
                    deleteBackup(
                        content.effects,
                        content.setEffects,
                        selected
                    )
                }

            commandBox.setCommand('');
        }
    
        if(commandBox.command === 'clear-zoom')
            {
                if(itemExists(content.imgBackup,selected))
                {
                    
                const effects = canvasEffRefs.current[selected]
                const canvas = canvasRefs.current[selected]
                const ctx = canvas.getContext('2d');
                ctx.putImageData(copy.current[selected],0,0)

                const backup = getItemWithId(content.imgBackup,selected)
                
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
                        content.effects,
                        content.setEffects,
                        {
                            id:selected,
                            data: foreground
                        }
                    )

                    deleteBackup(content.imgBackup,content.setImgBackup,selected)
                    updateItem(content.images,content.setImages,selected,background)
                }
    
                commandBox.setCommand('');
            }
    
    if (commandBox.command === 'save') {
        const canvas = canvasRefs.current[selected]
        const effects = canvasEffRefs.current[selected]
        blendAndSave(effects,canvas)
        commandBox.setCommand('');
    }
    }, [commandBox]);

    return (
        <div className="image-viewer-grid">
          {content.images.map((_, i) => (
            <div className={"canv-container-grid "+isSelected(i)} key={i}>
              <canvas
                className={"canv-effects-grid "+settings.cursor}
                ref={(el) => (canvasEffRefs.current[i] = el)}
              />
              <canvas
                className="canv-true-grid"
                ref={(el) => (canvasRefs.current[i] = el)}
              />
            </div>
          ))}
        </div>
      );
}

export default GridView;