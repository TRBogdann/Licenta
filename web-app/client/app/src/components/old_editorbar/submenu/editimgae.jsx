import { useEffect, useState } from "react";
import {getNextItem} from "../../../tools/mylist";
import { HexColorPicker } from "react-colorful";
import { changeTool, changeToolProps } from "../../../tools/editor";
import { absoluteImage, absStdImage, negativeActivations, pozitiveActivations, standardizeImage } from "../../../tools/myimage";

function EditImage(props)
{
    
    const [color, setColor] = useState("#aabbcc");
    const [pensize,setPensize] = useState(1);

    useEffect(()=>
    {
        const tools = props.tools
        if(tools.currentTool.toolname==='pen')
        {
            changeToolProps({'color':color},tools.setCurrentTool)
        }
    },[color])

    useEffect(()=>
    {
        if(props.commandBox.command==='reset_color')
        {
            setColor(props.tools.currentTool.properties.color)
            props.commandBox.setCommand('')
        }
    },[props.commandBox])

    useEffect(()=>
    {
        changeToolProps({'color':color,'pensize':pensize},props.tools.setCurrentTool)
    },[pensize])
    return(
        <div>
            <button onClick={()=>getNextItem(
                props.edit['cmaps'],
                props.edit['mapIndex'],
                props.edit['setMapIndex']
            )}>Change map</button>
            <HexColorPicker color={color} onChange={setColor} />
            <button onClick={()=>{
                const tools = props.tools
                changeTool('select',tools.setCurrentTool);
            }}>Cursor Mode</button>
            <button
            onClick={()=>{
                const tools = props.tools
                changeTool('pen',tools.setCurrentTool);
                changeToolProps({'color':color,'pensize':pensize},tools.setCurrentTool)
            }}>Pen Up</button>
            <button
            onClick={()=>{
                const tools = props.tools
                changeTool('colorPicker',tools.setCurrentTool);
            }} 
            >Pick Color</button>
            <button onClick={()=>props.commandBox.setCommand('clear')}>Clear</button>
            <button
            onClick={()=>{
                const tools = props.tools
                changeTool('erase',tools.setCurrentTool);
            }} >
                Erase
            </button>
            <div>{pensize}</div>
            <button onClick={()=>
                {
                    if(pensize<=1)
                        return
                    setPensize(pensize-1)
                }
            }>Down</button>
            <button onClick={()=>
                {
                    if(pensize>=255)
                        return
                    setPensize(pensize+1)
                    console.log('here')
                }
            }>Up</button>
            <button onClick={()=>{
                const tools = props.tools
                changeTool('zoom',tools.setCurrentTool);
            }} >
                Zoom
            </button>
            <button onClick={
                ()=>
                {
                    props.commandBox.setCommand('reset_zoom');
                }
            }>
                Clear Zoom
            </button>
            <button onClick={()=>
                {
                    props.edit.setCorrection({run:null});
                }
            }>
                No Correction
            </button>
            <button
            onClick={()=>
                {
                    props.edit.setCorrection({run:negativeActivations});
                }}
            >
                Negative Activations
            </button>
            <button
            onClick={()=>
                {
                    props.edit.setCorrection({run:pozitiveActivations});
                }} 
            >
                Pozitive Activations
            </button>
            <button
            
            onClick={()=>
                {
                    const func = (c,a,b)=>
                        {
                            standardizeImage(c,a,b,'minmax')
                        }
                    props.edit.setCorrection({run:func})
                }}>
                Standard Activations
            </button>
            <button
            onClick={()=>
                {
                    props.edit.setCorrection({run:absoluteImage});
                }}>
                Absolute Activations
            </button>
            <button
            
            onClick={()=>
                {
                    const func = (c,a,b)=>{absStdImage(c,a,b,'minmax')}
                    props.edit.setCorrection({run:func});
                }}>
                StdAbs
            </button>
            <div>{props.edit.overlayTh}</div>
            <button onClick={()=>props.commandBox.setCommand('th-down')}>Down Th</button>
            <button onClick={()=>props.commandBox.setCommand('th-up')}>Up Th</button>
        </div>
    )
}

export default EditImage;