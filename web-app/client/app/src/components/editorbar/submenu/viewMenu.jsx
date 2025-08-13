import { overlay } from "../../../tools/myimage";
import CustomLi from "../customMenu/customli";
import './temp.css'
function ViewMenu(props)
{
    const commandBox = props.data.commandBox;
    const settings = props.data.settings;
    const load = props.data.settings.hasMask && props.data.settings.hasActivation;
    return (
<aside class="vertical-sidebar"> 
    <input type="checkbox" role="switch" id="checkbox-input" class="checkbox-input" checked />
    <nav>
        <section class="sidebar__wrapper">
            <ul class="sidebar__list list--primary">
                <li class="sidebar__item item--heading">
                    <h2 class="sidebar__item--heading">View Mode</h2>
                </li>
                <CustomLi img='/logos/normal.svg' name='Normal' onClick={()=>{
            if(settings.viewMode==='overlay')
            {
                commandBox.setCommand('delete-backup')
            }
            settings.setViewMode('normal')}}></CustomLi>
                <CustomLi img='/logos/grid.svg' name='Grid'
                onClick={()=>{
                    if(settings.viewMode==='overlay')
                        {
                            commandBox.setCommand('delete-backup')
                        }
                        settings.setViewMode('grid')}}></CustomLi>
                <CustomLi img='/logos/overlay.svg' name='Overlay'
                onClick={()=>{
                    commandBox.setCommand('delete-backup')
                    settings.setViewMode('overlay')}}></CustomLi>
            </ul>

            {load?
                    <ul class="sidebar__list list--secondary">
                    <li class="sidebar__item item--heading">
                        <h2 class="sidebar__item--heading">Content</h2>
                    </li>
        {
            props.data.settings.mode==='activation'?
        <CustomLi img='/logos/mask.svg' name='Masks' onClick={()=>commandBox.setCommand('get-masks')}></CustomLi>:
        <CustomLi img='/logos/activation.svg' name='Activations' onClick={()=>commandBox.setCommand('get-activations')}></CustomLi>
        }

        {
            settings.viewMode==='overlay'?
            <li class="sidebar__item">
            <div class="sidebar__link"> 
            <span class="icon">
            <object type="image/svg+xml" data='/logos/threshold.svg'></object>
            </span> 
            <div class="text2">
            Threshold:  <input 
            type="number" 
            min="0" 
            step="0.05" 
            max = "1"
            value={settings.overlay} 
            onChange={(e) => settings.setOverlay(Number(e.target.value))}
            className="input-template"
        /></div>
            </div> 
            </li> :
            <></>
        }
        </ul>
        :<></>
        }
            <ul class="sidebar__list list--secondary">
                <li class="sidebar__item item--heading">
                    <h2 class="sidebar__item--heading">Save</h2>
                </li>
                <CustomLi img='/logos/save.svg' name='Save' onClick={()=>commandBox.setCommand('save')}></CustomLi>
            </ul>
        </section>
    </nav>
</aside>
    )
}

export default ViewMenu;
