import { clearZoom } from "./myimage";

/**
 * 
 * @param {Array} vector 
 * @param {Number} index 
 * @param {Function} setIndex 
 */
export function getNextItem(vector, index, setIndex) {
    setIndex(prev => (prev >= vector.length - 1 ? 0 : prev + 1));
}

export function updateItem(vector,setVector,index,newItem){
    setVector(prev => {
      const newVector = [...prev]; 
      newVector[index] = newItem;        
      return newVector;
    });
  };

export function itemExists(vector,id)
{
    const index = vector.findIndex(obj => obj.id === id);
    return index > -1 
}

export function getItemWithId(vector,id)
{
    const index = vector.findIndex(obj => obj.id === id);
    return vector[index]
}


export function createBackup(vector,setVector,newObj)
{
    setVector(prev =>
    {

        const index = prev.findIndex(obj => obj.id === newObj.id);
        if (index === -1) 
            return [...prev, newObj];

        const updated = [...prev];
        updated[index] = newObj;
        return updated;
    }
    )
}

export function deleteBackup(vector, setVector, idToDelete) {
    setVector(prev => prev.filter(obj => obj.id !== idToDelete));
}
