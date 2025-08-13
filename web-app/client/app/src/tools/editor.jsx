
export function changeTool(toolname,setTool)
{
    setTool(prev => ({ ...prev, toolname: toolname }));
}

export function changeToolProps(properties,setTool)
{
    setTool(prev => ({ ...prev, properties: properties }));
}

