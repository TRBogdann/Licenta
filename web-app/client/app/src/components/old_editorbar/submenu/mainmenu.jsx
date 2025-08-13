
function MainMenu(props)
{
    return (
        <div>
        <button onClick={()=>props.commandBox.setCommand('normal-view')}>Normal</button>
        <button onClick={()=>props.commandBox.setCommand('grid-view')}>Grid</button>
        <button onClick={()=>props.commandBox.setCommand('full-overlay-view')}>Overlay Full</button>
        <button onClick={()=>props.commandBox.setCommand('side-overlay-view')}>Overlay Side</button>
        <button onClick={()=>props.commandBox.setCommand('get-masks')}>Mask</button>
        <button onClick={()=>props.commandBox.setCommand('get-activations')}>Activations</button>
        <button
        onClick={()=>props.commandBox.setCommand('save')}>Save</button>
        </div>
    )
}
export default MainMenu;