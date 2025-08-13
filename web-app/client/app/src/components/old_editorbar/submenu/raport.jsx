
function Raport(props)
{

    function getTable(classes, probs)
    {
        const arr = []
        let mx = -1;
        let index = -1
        for(let i=0; i<classes.length; i++)
        {
            arr.push(<div>{classes[i]}:{probs[i]}</div>)
            if(probs[i]>mx)
            {
                index = i
                mx = probs[i]
            }
        }
        const target = <div>Prediction:{classes[index]}</div>

        return (
            <div>                
                {target}
                {arr}
            </div>
        )
    }
    return(
        <div>
            <h1>Classification raport</h1>
            {getTable(props.classes,props.probs)}
        </div>
    )
}

export default Raport