import { HexColorPicker } from "react-colorful";
import CustomLi from "../customMenu/customli";

function EditMenu(props)
{
    const tool = props.data.tool;
    const commandBox = props.data.commandBox;
    const palette = props.data.palette;
    const cmaps = ['normal', 'viridis', 'plasma', 'inferno', 'magma', 'jet', 'hot', 'cool']

    return(
    <div>
      <div className="center-container">
      <HexColorPicker color={tool.color} onChange={tool.setColor} />
        </div>
      <aside class="vertical-sidebar"> 
    <input type="checkbox" role="switch" id="checkbox-input" class="checkbox-input" checked />
    <nav>
        <section class="sidebar__wrapper">
            <ul class="sidebar__list list--primary">

                <li class="sidebar__item item--heading">
                    <h2 class="sidebar__item--heading">Tools</h2>
                </li>
                <CustomLi img='/logos/select.svg' name='Select'onClick={()=>
            {
                tool.setToolName('select');
            }}></CustomLi>
                <CustomLi img='/logos/pen.svg' name='Pen'onClick={()=>
            {
                tool.setToolName('pen');
            }}></CustomLi>

<li class="sidebar__item">
            <div class="sidebar__link"> 
            <span class="icon">
            <object type="image/svg+xml" data='/logos/pensize.svg'></object>
            </span> 
            <div class="text2">
            Pensize:  <input 
            type="number" 
            min="1" 
            step="1" 
            max = "1000"
            value={tool.pensize} 
            onChange={(e) => tool.setPensize(Number(e.target.value))}
            className="input-template"
        /></div>
            </div> 
            </li>
                <CustomLi img='/logos/color-picker.svg' name='Color Picker'
                onClick={()=>
                    {
                        tool.setToolName('colorPicker');
                    }}></CustomLi>
                <CustomLi img='/logos/eraser.svg' name='Eraser'
                onClick={()=>
                    {
                        tool.setToolName('erase');
                    }}></CustomLi>
                <CustomLi img='/logos/zoom.svg' name='Zoom'
                onClick={()=>
                    {
                        tool.setToolName('zoom');
                    }}></CustomLi>
            </ul>
            <ul class="sidebar__list list--secondary">
                <li class="sidebar__item item--heading">
                    <h2 class="sidebar__item--heading">Clear</h2>
                </li>
                <CustomLi img='/logos/clear.svg' name='Clear Image'
                      onClick={()=>
                        {
                            commandBox.setCommand('clear');
                        }
                        }></CustomLi>
                <CustomLi img='/logos/clear-zoom.svg' name='Clear Zoom'
                      onClick={()=>
                        {
                            commandBox.setCommand('clear-zoom');
                        }
                        }></CustomLi>
            </ul>
            <ul class="sidebar__list list--secondary">
                <li class="sidebar__item item--heading">
                    <h2 class="sidebar__item--heading">Palette</h2>
                </li>
                <li class="sidebar__item">
                <div class="sidebar__link"> 
                    <span class="icon">
                    <object type="image/svg+xml" data='/logos/cmap.svg'></object>
                    </span> 
                    <div class="text2">
                    Color Map:</div>
                </div> 
                </li>
                <li class="sidebar__item">
                <div class="sidebar__link"> 

                    <select className="input-template-big" id="cmap-select" value={palette.cmap} onChange={(e)=>
            {
                palette.setCmap(e.target.value)
            }
        }>
            {cmaps.map((cmap) => (
            <option key={cmap} value={cmap}>
                {cmap}
            </option>
            ))}
        </select></div>

                </li>
                <li class="sidebar__item">
                <div class="sidebar__link"> 
                    <span class="icon">
                    <object type="image/svg+xml" data='/logos/activation.svg'></object>
                    </span> 
                    <div class="text2">
                    Activation:</div>
                </div> 
                </li>
                <li class="sidebar__item">
                <div class="sidebar__link"> 

                    <select className="input-template-big" id="correction-select" value={palette.correction} onChange={(e)=>
            {
                palette.setCorrection(e.target.value)
            }}>
        <option value="none">none</option>
        <option value="standard">standard</option>
        <option value="negative">negative</option>
        <option value="pozitive">pozitive</option>
        <option value="absolute">absolute</option>
        <option value="standard-absolute">standard-absolute</option>
      </select></div>
                </li>
            </ul>


        </section>
    </nav>
</aside>
    </div>
    )
}

export default EditMenu;