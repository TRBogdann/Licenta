import { useState } from "react";
import ViewMenu from "./submenu/viewMenu";
import EditMenu from "./submenu/editMenu";
import ResultMenu from "./submenu/resultMenu";
import './editorbar.css'

function EditorBar(props)
{
    const [subMenuIndex,setSubMenuIndex] = useState(2);

    function getSubMenu(id) {
        switch (id) {
            case 0:
                return (
                    <ViewMenu data={props.data}/>
                )

            case 1:
                return (
                    <EditMenu data={props.data}/>
                );
            default:
                return (
                    <ResultMenu result={props.data.result}/>
                );
        }
    }

    return(
    <div className='editor-border'>
    <div className="editor-bar">
        <div className="editor-controls">
            <div onClick={()=>setSubMenuIndex(0)}>
            <img alt='none' src='logos/menu.svg' ></img>
            </div>
            <div onClick={()=>setSubMenuIndex(1)}>
            <img alt='none' src='logos/edit.svg' ></img>
            </div>
            <div onClick={()=>setSubMenuIndex(2)}>
            <img alt='none' src='logos/result.svg' ></img>
            </div>
        </div>

            {getSubMenu(subMenuIndex)}
    </div>
    </div>

    )
}

export default EditorBar;
