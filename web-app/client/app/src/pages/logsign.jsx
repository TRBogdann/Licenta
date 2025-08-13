import { useState } from "react";
import './logsign.css';
import { useNavigate } from "react-router-dom";

function LogSign()
{
const [classVal,setClassVal] = useState("");

const [user,setUser] = useState({username:"",password:""});

function send(data)
{
    if(data.username!=="" && data.password!=="")
    {
        const formData = new FormData();
        formData.append("username",data.username);
        formData.append("password",data.password);

        const req = new XMLHttpRequest();
        
        req.open("POST","http://localhost:2020/login");
        
        req.onload = ()=>
        {
          if(req.status === 200) {
            window.localStorage.setItem("session_id",JSON.parse(req.responseText).session_id);
            window.location.pathname="/";
          }
        }
        
        req.send(formData);
    }
}


const [userData,setUserData] =useState({
  firstname:"",
  lastname:"",
  username:"",
  email:"",
  password:"",
  confirmPassword:"",
});

function checkData(data)
{   
  console.log(data);
  return true;
}

function sendForm(data)
{
  if(checkData(data))
  {
      const req = new XMLHttpRequest();
      const formData = new FormData();
      
      for(const key in data)
      {
          formData.append(key,data[key]);
      }

      fetch('http://localhost:8080/sign', {
        method: 'POST',
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }
}

    return (
        <div className="contain-login">
        <div className={"wrapper"+classVal}>
        <span className="bg-animate"></span>
        <span className="bg-animate2"></span>
  
        
        <div className="form-box login">
          <h2 className="animation" style={{'--i': 0, '--j': 21}}>Login</h2>
          <form >
            <div className="input-box animation" style={{'--i': 1, '--j': 22}}>
              <input type="text" required onChange={(e)=>{user.username = e.target.value; setUser(user);}}/>
              <label >Username or Email</label>
              <i className="bx bxs-user"></i>
            </div>
            <div className="input-box animation" style={{'--i': 2, '--j': 23}}>
              <input onChange={(e)=>{user.password = e.target.value; setUser(user);}} type="password" required />
              <label>Password</label>
              <i className="bx bxs-lock-alt"></i>
            </div>
            <button type="submit" className="btn animation" style={{'--i': 3, '--j': 24}} onClick={(e)=>{e.preventDefault(); send(user);}}>
              Login
            </button>
            <div className="logreg-link animation" style={{'--i': 4, '--j': 25}}>
              <div>
                <a href="#" onClick={(e)=>{e.preventDefault();setClassVal(" active")}}>Sign Up</a>
                <span>{" here if you don't have an account"}</span>
              </div>
            </div>
          </form>
        </div>
  
        <div className="info-text login">
          <h2 className="animation" style={{'--i': 0, '--j': 20}}>Welcome Back!</h2>
          <p className="animation" style={{'--i': 1, '--j': 21}}>
            We are happy to see you again!
          </p>
        </div>
  
        <div className="form-box register">
          <h2 className="animation" style={{'--i': 17, '--j': 0}}>Sign Up</h2>
          <form>
            <div className="input-box animation" style={{'--i': 18, '--j': 1}}>
              <input type="text" required onChange={(ev)=>{
            userData.firstname = ev.target.value;
            setUserData(userData)
        }} />
              <label>First Name</label>
              <i className="bx bx-child"></i>
            </div>
            <div className="input-box animation" style={{'--i': 19, '--j': 2}}>
              <input type="text" required         onChange={(ev)=>{
            userData.lastname = ev.target.value;
            setUserData(userData)
        }}/>
              <label>Last Name</label>
              <i className="bx bxs-wink-smile"></i>
            </div>
            <div className="input-box animation" style={{'--i': 20, '--j': 3}}>
              <input type="email" required         onChange={(ev)=>{
            userData.email = ev.target.value;
            setUserData(userData)
        }}/>
              <label>Email</label>
              <i className="bx bxs-envelope"></i>
            </div>
            <div className="input-box animation" style={{'--i': 21, '--j': 4}}>
              <input type="text" required         onChange={(ev)=>{
            userData.username = ev.target.value;
            setUserData(userData)
        }}/>
              <label>Username</label>
              <i className="bx bxs-user"></i>
            </div>
            <div className="input-box animation" style={{'--i': 22, '--j': 5}}>
              <input type="password" required         onChange={(ev)=>{
            userData.password = ev.target.value;
            setUserData(userData)
        }}/>
              <label>Password</label>
              <i className="bx bxs-lock-alt"></i>
            </div>
            <div className="input-box animation" style={{'--i': 23, '--j': 6}}>
              <input type="password" required        onChange={(ev)=>{
            userData.confirmPassword = ev.target.value;
            setUserData(userData)
        }}/>
              <label>Confirm Password</label>
              <i className="bx bxs-lock"></i>
            </div>
            <button type="submit" className="btn animation" style={{'--i': 24, '--j': 7}} onClick={(ev)=>
            {
                ev.preventDefault();
                sendForm(userData);    
            }
          }>
              Sign Up
            </button>
            <div className="logreg-link animation" style={{'--i': 25, '--j': 8}}>
              <p>
                Already have an account?
                <a href="#" onClick={()=>setClassVal("")} className="login-link">Login</a>
              </p>
            </div>
          </form>
        </div>
  
        <div className="info-text register">
          <h2 className="animation" style={{'--i': 17, '--j': 0}}>Welcome!</h2>
          <p className="animation" style={{'--i': 18, '--j': 1}}>
            {"Meesage 2!"}
          </p>
        </div>
      </div>
      </div>
    );
}

export default LogSign