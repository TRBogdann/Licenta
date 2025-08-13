import './navbar.css'
import {useNavigate } from 'react-router-dom';

function Navbar(props)
{
    const navigate = useNavigate();

    return(
        <div className='app-navbar'>

        <div className='resizer'>
        <div className='plasma-border'>
        <div className='logo-wrapper'>
        <img className='dna-logo ' src={props.image} alt='not found'></img>
        </div>
        </div>
        </div>

        <div className='app-links'>
        <div>Library</div>
        <div onClick={()=>{navigate("/tools", { replace: true });}}>Tools</div>
        <div>About</div>
        <div>Account</div>
        <div onClick={props.setColor}>Theme</div>
        </div>

        <div className='resizer'>
        <button className='log-button' onClick={()=>{navigate("/logsign", { replace: true });}}>
            Log In
        </button>
        </div>

        </div>
    );
}

export default Navbar;