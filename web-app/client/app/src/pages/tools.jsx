import { useNavigate } from 'react-router-dom';
import './tools.css'

function Tools(props)
{
    const navigate = useNavigate();
    
    return (
        <div className="tools-container">

            <div className="my-tools">
            

            <div className='plasma-border refresh' 
            onClick={()=>{navigate("/", { replace: true });}}>
            <div className='logo-wrapper'>
            <img className='dna-logo ' src={props.image} alt='not found'></img>
            </div>
            </div>
            
            <div className='tools-arr'>▲</div>

            <div className='actual-tools'>


            <img 
            onClick={()=>{
                props.setServerRoute({mask:'http://localhost:8080/all',activation:'http://localhost:8080/all_activ',type:''});
                navigate("/load", { replace: true });
            }}
            className='tool-icon' src={'/logos/bicon.png'} alt='not found'></img>
            <img className='tool-icon' src={'/logos/brain(1).png'} alt='not found'
             onClick={()=>{
                props.setServerRoute({mask:'',activation:'http://localhost:8080/brain'});
                navigate("/load", { replace: true });
            }}></img>
            <img className='tool-icon' src={'/logos/lung.png'} alt='not found'
            onClick={()=>{
                props.setServerRoute({mask:'',activation:'http://localhost:8080/chest',type:''});
                navigate("/load", { replace: true });
            }}></img>
            <img className='tool-icon' src={'/logos/eye.png'} alt='not found'
                    onClick={()=>{
                        props.setServerRoute({mask:'',activation:'http://localhost:8080/eye',type:''});
                        navigate("/load", { replace: true });
                    }}>

                    </img>
            <img className='tool-icon' src={'/logos/kidney.png'} alt='not found'
            onClick={()=>{
                props.setServerRoute({mask:'',activation:'http://localhost:8080/kidney',type:''});
                navigate("/load", { replace: true });
            }}></img>



            </div>

            <div className='tools-arr'>▼</div>

            </div>


            <div className="current-tool"></div>
        </div>
    );
}

export default Tools;