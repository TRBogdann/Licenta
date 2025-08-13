import './maineditor.css'
import FullEditor from './fulleditor';

function EditorBar(props)
{


    function getEditor(viewMode,classes,probs)
    {
        switch(viewMode)
        {
            default: return <FullEditor classes={classes} probs={probs} edit={props.edit} tools={props.tools} commandBox={props.commandBox}/>;
        }
    }
    return (
        <>
        <div className='editor-border'>
        {getEditor(props.viewMode,props.classes,props.probs)}
        </div>
        </>
    );
}

export default EditorBar;