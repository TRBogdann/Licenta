import { useEffect, useRef, useState } from "react";
import { blendAndSave, blendPixels, changeImage, clearZoom, getImageFromCanvas, rewriteCanvas } from "../../tools/myimage";
import { createBackup, getItemWithId, itemExists, updateItem } from "../../tools/mylist";
import { changeTool, changeToolProps } from "../../tools/editor";
import applyMap from "../../tools/colormap";

function GridViewer(props) {
  const canvasRefs = useRef([]);
  const canvasEffRefs = useRef([]);
  const drawing = useRef([]); 
  const lastPos = useRef([]);
  const old = useRef([])
  const zoomStart = useRef([]);
  const zoomEnd = useRef([]);
  const zooming = useRef([])
  const [selected,setSelected] = useState(0)


  function isSelected(index)
  {
    if(index===selected)
        return 'selected-box';
    
    return '';
  }

  function rgbToHex(r, g, b) {
    return "#" + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
}

  // Load images into canvases
  useEffect(() => {
    const controller = new AbortController();
    canvasRefs.current.length = props.images.length;
    canvasEffRefs.current.length = props.images.length;

    for (let i = 0; i < canvasEffRefs.current.length; i++) {
      const canvasTrue = canvasRefs.current[i];
      const canvasEff = canvasEffRefs.current[i];
      const ctxTrue = canvasTrue.getContext("2d");
      const ctxEff = canvasEff.getContext("2d");

      const img = new Image();
      img.onload = () => {
        if (controller.signal.aborted) return;

        canvasTrue.width = img.width;
        canvasTrue.height = img.height;
        canvasEff.width = img.width;
        canvasEff.height = img.height;
        ctxTrue.drawImage(img, 0, 0);

        const mapIndex = props.edit['mapIndex'];
        if (props.edit['cmaps'][mapIndex] !== 'normal' && i !== 0 ) {
            applyMap(canvasTrue, props.edit['cmaps'][mapIndex]);
        }

        if (itemExists(props.backup.effects,i)) {
            const img2 = new Image();
            img2.onload = () => {
                if (controller.signal.aborted) return;
                ctxEff.drawImage(img2, 0, 0);
            };
            const temp = props.backup.effects;
            img2.src = getItemWithId(temp, i).data;
        } else {
            ctxEff.clearRect(0, 0, img.width, img.height);
        }
      };
      img.src = props.images[i];
    }

    return () => {
        controller.abort();
    };
  }, [props.images,props.edit]);



  function eraseAt(ctx,x, y, size) {
    ctx.clearRect(x - size / 2, y - size / 2, size, size);
}

useEffect(()=>
{
    if(!props.tools)
        return;

    if(props.tools.currentTool.toolname !== 'select')
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
},[props.tools])


useEffect(()=>
{
    if(!props.tools)
        return;

    if(props.tools.currentTool.toolname !== 'colorPicker')
        return

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

            changeTool('pen',props.tools.setCurrentTool)
            changeToolProps({'color':hexColor},props.tools.setCurrentTool)
            props.commandBox.setCommand('reset_color');
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
    
},[props.tools])

useEffect(() => {
    if (!props.tools || props.tools.currentTool.toolname !== 'zoom') return;

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

        // Clear and redraw all previous rectangles
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

        if (start && end) {
            
            const w = Math.abs(end.x - start.x)
            const h = Math.abs(end.y - start.y)

            ctxFg.putImageData(old.current[index], 0, 0);

            if(canvasFg.width<w || canvasFg.height<h || w<32 || h<32)
                return;

            const backup = props.backup
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
                    backup.keep,
                    backup.setKeep,
                    {
                        id:index,
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
                        id:index,
                        data: newEff.image
                    }
                )
    
                updateItem(props.images,props.setImages,index,newImg.image)
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
}, [props.tools]);


  useEffect(() => {

    if(!props.tools)
        return;

    if (
        props.tools.currentTool.toolname !== 'pen' &&
        props.tools.currentTool.toolname !== 'erase'
    ) return;

    const color = props.tools.currentTool.properties?.color || "black";
    const pensize = props.tools.currentTool.properties?.pensize || 2;

    const handleMouseDown = props.tools.currentTool.toolname==='pen'?(e, index) => {
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


    const handleMouseMove = props.tools.currentTool.toolname==='pen'?(e, index) => {
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

      const effVector = props.backup.effects;
      const setEffects = props.backup.setEffects;
      createBackup(
          effVector,
          setEffects,
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
  }, [props.tools]);

useEffect(() => {
    
    if (props.commandBox.command === 'clear') {
            const canvas = canvasEffRefs.current[selected];
            const ctx = canvas.getContext('2d')
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
  
        props.commandBox.setCommand('');
    }

    if(props.commandBox.command === 'reset_zoom')
        {
            if(itemExists(props.backup.keep,selected))
            {


            const canvasTrue = canvasRefs.current[selected]
            const canvasEff = canvasEffRefs.current[selected]

            const backup = getItemWithId(props.backup.keep,selected)
            
            const foreground = clearZoom(
                backup,
                backup.fg_img,
                canvasEff
                )

            const background = clearZoom(
                backup,
                backup.bg_img,
                canvasTrue
                )
            

                const effVector = props.backup.effects
                const setEffects = props.backup.setEffects
                    createBackup(
                        effVector,
                        setEffects,
                        {
                            id:selected,
                            data: foreground
                        }
                    )
                updateItem(props.images,props.setImages,selected,background)
            }

            props.commandBox.setCommand('');
        }

        if (props.commandBox.command === 'save') {
            const canvasTrue = canvasRefs.current[selected]
            const canvasEff = canvasEffRefs.current[selected]
            blendAndSave(canvasEff,canvasTrue)
            props.commandBox.setCommand('');
        }
}, [props.commandBox]);

  return (
    <div className="image-viewer-grid">
      {props.images.map((_, i) => (
        <div className={"canv-container-grid "+isSelected(i)} key={i}>
          <canvas
            className="canv-effects-grid"
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

export default GridViewer;
