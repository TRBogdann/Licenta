
function ResultMenu(props)
{
    const result = props.result; 
    function getTable(classes, probs)
    {
        if(classes.length===0 || probs.length===0)
            return (
                <div>                
                    No Data
                </div>
            )

        const arr = []
        let mx = -1;
        let index = -1
        for(let i=0; i<classes.length; i++)
        {
            
            arr.push(<li class="sidebar__item item--heading"><h2 class="sidebar__item--heading">{classes[i]}:{probs[i]}</h2></li>)
            if(probs[i]>mx)
            {
                index = i
                mx = probs[i]
            }
        }
        const target = <li class="sidebar__item item--heading"><h1>Prediction:{classes[index]}</h1></li>

        return (
            <>             
                {target}
                {arr}
            </> 
        )
    }
    return(
<aside class="vertical-sidebar"> 
    <input type="checkbox" role="switch" id="checkbox-input" class="checkbox-input" checked />
    <nav>
        <section class="sidebar__wrapper">
            <ul class="sidebar__list list--primary">
                {getTable(result.labels,result.probs)}
            </ul>
        </section>
    </nav>
</aside>
    )
}

export default ResultMenu;
