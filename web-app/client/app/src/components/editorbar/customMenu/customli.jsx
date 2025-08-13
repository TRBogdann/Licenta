
function CustomLi(props)
{
    return(
        <li class="sidebar__item" onClick={props.onClick}> 
            <a class="sidebar__link" href="#"> 
            <span class="icon">
                <object type="image/svg+xml" data={props.img}></object>
            </span> 
            <span class="text">{props.name}</span> 
            </a> 
        </li>
    )
}

export default CustomLi;