import { useEffect, useState } from "react";
import EditImage from "./submenu/editimgae";
import MainMenu from "./submenu/mainmenu";
import Raport from "./submenu/raport";

function FullEditor(props)
{
    const [current,setCurrent] = useState(<Raport classes={props.classes} probs={props.probs}/>)
    const [componentIndex,setComponentIndex] = useState(2);

    useEffect(()=>
    {
        switch (componentIndex)
        {
            case 0:
                setCurrent(<MainMenu commandBox={props.commandBox}/>)
                break;
            case 1:
                setCurrent(<EditImage edit={props.edit} tools={props.tools} commandBox={props.commandBox}/>)
                break;
            default:
                setCurrent(<Raport classes={props.classes} probs={props.probs}/>)
        }
    },[props,componentIndex])

    useEffect(()=>
    {
        setCurrent(<Raport classes={props.classes} probs={props.probs}/>)
    },[props.classes,props.probs])


    return (
    <div className="editor-bar">
        <div className="editor-controls">
            <img className="btn-template-short" alt='none' src="/editor_images/home_w.png" onClick={()=>setComponentIndex(0)}></img>
            <img className="btn-template-short" alt='none' src="/editor_images/edit_2.png" onClick={()=>setComponentIndex(1)}></img>
            <img className="btn-template-short" alt='none' src="/editor_images/raport_w.png" onClick={()=>setComponentIndex(2)}></img>
        </div>
        {current}
    </div>
    );
}

export default FullEditor