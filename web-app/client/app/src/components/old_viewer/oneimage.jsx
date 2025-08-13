import { useEffect, useRef, useState } from 'react';
import applyMap from '../../tools/colormap';
import { changeTool, changeToolProps } from '../../tools/editor';
import { blendAndSave, blendPixels, changeImage, clearZoom, getImageFromCanvas } from '../../tools/myimage';
import { createBackup, getItemWithId, itemExists, updateItem } from '../../tools/mylist';

function OneImageViewer(props) {
    const canvasTrue = useRef();
    const canvasEff = useRef();
    const [imgIndex, setImgIndex] = useState(0);
    const [cursor, setCursor] = useState('');
    
    function decreaseIndex() {
        if (props.images.length > 0 && imgIndex > 0) {
            const effVector = props.backup.effects
            const setEffects = props.backup.setEffects
            createBackup(
                effVector,
                setEffects,
                {
                    id:imgIndex,
                    data: getImageFromCanvas(canvasEff.current)
                }
            )
            setImgIndex(imgIndex - 1);
        }
    }

    function increaseIndex() {
        if (props.images.length > 0 && imgIndex < props.images.length - 1) {
            const effVector = props.backup.effects
            const setEffects = props.backup.setEffects
            createBackup(
                effVector,
                setEffects,
                {
                    id:imgIndex,
                    data: getImageFromCanvas(canvasEff.current)
                }
            )
            setImgIndex(imgIndex + 1);
        }
    }

    useEffect(() => {
        if (props.tools.currentTool.toolname === 'pen') {
            setCursor('paint-mode');
        } else {
            setCursor('');
        }
    }, [props.tools]);

    useEffect(() => {
        let isMounted = true;
    
        if (props.images.length > 0) {
            const canvas = canvasTrue.current;
            const effects = canvasEff.current;
            const ctx = canvas?.getContext('2d');
            const img = new Image();
    
            img.onload = () => {
                if (!isMounted || !canvas || !ctx) return;
    
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
    
                const mapIndex = props.edit['mapIndex'];
                if (props.edit['cmaps'][mapIndex] !== 'normal' && imgIndex !== 0) {
                    console.log(imgIndex)
                    console.log(props.ranges[imgIndex])
                    if(props.edit.correction.run!=null)
                    {
                        props.edit.correction.run(canvas,props.ranges[imgIndex].a,props.ranges[imgIndex].b)
                    }
                    applyMap(canvas, props.edit['cmaps'][mapIndex]);
                }
    
                if (itemExists(props.backup.effects, imgIndex)) {
                    const img2 = new Image();
                    img2.onload = () => {
                        if (!isMounted || !effects) return;
    
                        const effCtx = effects.getContext('2d');
                        effects.width = img2.width;
                        effects.height = img2.height;
                        effCtx.drawImage(img2, 0, 0);
                    };
                    const temp = props.backup.effects;
                    img2.src = getItemWithId(temp, imgIndex).data;
                } else if (effects) {
                    effects.width = img.width;
                    effects.height = img.height;
                    const effCtx = effects.getContext('2d');
                    effCtx.clearRect(0, 0, effects.width, effects.height);
                }
            };
    
            img.src = props.images[imgIndex];
        }
    
        return () => {
            isMounted = false;
        };
    }, [props.images, imgIndex, props.edit]);


    useEffect(() => {
        const canvas = canvasEff.current;

        if (!canvas ||(
            props.tools.currentTool.toolname !== 'pen' &&
            props.tools.currentTool.toolname !== 'erase'
        )
        ) return;

        
        const ctx = canvas.getContext('2d');
        let drawing = false;

        const startDrawing = (e) => {
            drawing = true;
            draw(e);
        };

        const endDrawing = () => {
            const effVector = props.backup.effects;
            const setEffects = props.backup.setEffects;
            createBackup(
                effVector,
                setEffects,
                {
                    id:imgIndex,
                    data: getImageFromCanvas(canvasEff.current)
                }
            )
            drawing = false;
            ctx.beginPath();
        };

        const draw = (e) => {
            console.log(drawing)
            if (!drawing) return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;

            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;

            ctx.lineWidth = props.tools.currentTool.properties.pensize || 5;
            ctx.lineCap = 'round';


            if (props.tools.currentTool.toolname==='erase') {
                ctx.globalCompositeOperation = 'destination-out';
                ctx.strokeStyle = 'rgba(0,0,0,1)';
            } 
            else {
                ctx.globalCompositeOperation = 'source-over';
                ctx.strokeStyle = props.tools.currentTool.properties.color || 'red';
            }

            ctx.lineTo(x, y);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(x, y);
        };

        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mouseup', endDrawing);
        canvas.addEventListener('mouseleave', endDrawing);
        canvas.addEventListener('mousemove', draw);

        return () => {
            canvas.removeEventListener('mousedown', startDrawing);
            canvas.removeEventListener('mouseup', endDrawing);
            canvas.removeEventListener('mouseleave', endDrawing);
            canvas.removeEventListener('mousemove', draw);
        };
    }, [props.tools, imgIndex]);

    useEffect(() => {
        if (props.commandBox.command === 'clear') {
            const ctx = canvasEff.current?.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, canvasEff.current.width, canvasEff.current.height);
            }
            props.commandBox.setCommand('');

            const effVector = props.backup.effects
            const setEffects = props.backup.setEffects
                createBackup(
                    effVector,
                    setEffects,
                    {
                        id:imgIndex,
                        data: getImageFromCanvas(canvasEff.current)
                    }
                )
        }
        if(props.commandBox.command === 'reset_zoom')
        {
            if(!itemExists(props.backup.keep,imgIndex))
            {
                props.commandBox.setCommand('')
                return
            }
            const backup = getItemWithId(props.backup.keep,imgIndex)
            
            const foreground = clearZoom(
                backup,
                backup.fg_img,
                canvasEff.current
                )

            const background = clearZoom(
                backup,
                backup.bg_img,
                canvasTrue.current
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
            updateItem(props.images,props.setImages,imgIndex,background)

            props.commandBox.setCommand('');
        }

        if (props.commandBox.command === 'save') {
            blendAndSave(canvasEff.current,canvasTrue.current)
            props.commandBox.setCommand('');
        }
    }, [props.commandBox]);

    // Color picker: on mouse down set color to pixel color under mouse if tool is colorPicker
    useEffect(() => {
        const canvas = canvasEff.current;
        if (!canvas) return;
        
        const ctxEff = canvasEff.current.getContext('2d');
        const ctxTrue = canvasTrue.current.getContext('2d');

        function rgbToHex(r, g, b) {
            return "#" + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
        }

        function onMouseDown(e) {
            if (props.tools.currentTool.toolname !== 'colorPicker') return;

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

        canvas.addEventListener('mousedown', onMouseDown);
        return () => {
            canvas.removeEventListener('mousedown', onMouseDown);
        };
    }, [props.tools]);

    useEffect(() => {
        const canvasFg = canvasEff.current;
        const canvasBg = canvasTrue.current;

        if (!canvasFg || !canvasFg ||
            props.tools.currentTool.toolname !== 'zoom')
            return;

        const ctxFg = canvasFg.getContext('2d');
        const ctxBg = canvasBg.getContext('2d');

        const old = ctxFg.getImageData(0,0,canvasFg.width,canvasFg.height)
        
        let x_start = 0,y_start = 0;
        let x_end = 0, y_end = 0;
        let zooming = false;

        const getStart = (e) => {
            zooming = true;
            const rect = canvasFg.getBoundingClientRect();
            const scaleX = canvasFg.width / rect.width;
            const scaleY = canvasFg.height / rect.height;

            x_start = Math.floor((e.clientX - rect.left) * scaleX);
            y_start = Math.floor((e.clientY - rect.top) * scaleY);

        };

        const getEnd = (e) => {
            if(!zooming)
                return;
            zooming = false;
            ctxFg.putImageData(old, 0, 0);

            const w = Math.abs(x_end - x_start)
            const h = Math.abs(y_end - y_start)

            if(canvasFg.width<w || canvasFg.height<h || w<32 || h<32)
                return;

            const backup = props.backup
            const ratio = canvasFg.width/canvasFg.height

            const fg_old = old
            const bg_old = ctxBg.getImageData(0,0,canvasBg.width,canvasBg.height)
            
            const newEff = changeImage(
                canvasFg,
                {'x':x_start,'y':y_start},
                {'x':x_end,'y':y_end},
                ratio)

            const newImg = changeImage(
                canvasBg,
                {'x':x_start,'y':y_start},
                {'x':x_end,'y':y_end},
                ratio)     
            
            createBackup(
                backup.keep,
                backup.setKeep,
                {
                    id:imgIndex,
                    start:{'x':x_start,'y':y_start},
                    end:{'x':x_end,'y':y_end},
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

            updateItem(props.images,props.setImages,imgIndex,newImg.image)
        };

        const draw = (e) => {
            if(!zooming)
                return;

            const rect = canvasFg.getBoundingClientRect();
            const scaleX = canvasFg.width / rect.width;
            const scaleY = canvasFg.height / rect.height;

            x_end = Math.floor((e.clientX - rect.left) * scaleX);
            y_end = Math.floor((e.clientY - rect.top) * scaleY);


            ctxFg.putImageData(old, 0, 0);

            const left = Math.min(x_start, x_end);
            const top = Math.min(y_start, y_end);
            const width = Math.abs(x_end - x_start);
            const height = Math.abs(y_end - y_start);
        
            if(canvasFg.width<width || canvasFg.height<height || width<32 || height<32)
                ctxFg.strokeStyle = 'red';
            else
                ctxFg.strokeStyle = 'green';
            ctxFg.lineWidth = 1;
        
            ctxFg.strokeRect(left, top, width, height);
        };

        canvasFg.addEventListener('mousedown', getStart);
        canvasFg.addEventListener('mouseup', getEnd);
        canvasFg.addEventListener('mouseleave', getEnd);
        canvasFg.addEventListener('mousemove', draw);

        return () => {
            canvasFg.removeEventListener('mousedown', getStart);
            canvasFg.removeEventListener('mouseup', getEnd);
            canvasFg.removeEventListener('mouseleave', getEnd);
            canvasFg.removeEventListener('mousemove', draw);
        };
    }, [props.tools, imgIndex]);

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

export default OneImageViewer;
