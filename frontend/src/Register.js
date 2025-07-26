import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import HamburgerMenu from './HamburgerMenu';

function Register() {
    
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [first_name, setFirstName] = useState('');
    const [last_name, setLastName] = useState('');
    const navigate = useNavigate();

    const register = async () => {
        const formData = { username, password, first_name, last_name };
        // ************* validate user input ***********************
        // no nulls
        if (!username || !password || !first_name || !last_name){
            alert('All fields are required to be filled out.');
            return;
        }

        // username validation
        const isAlphanumeric = /^[a-zA-Z0-9]+$/.test(username);
        if(username.length < 6 || !isAlphanumeric){
            alert('Username must be at least 6 characters in length and may only contain alphanumeric characters.')
            return;
        }
        
        // password validation
        // contains at least one uppercase, one lowercase, one number, onespecial character, and is at least 8 characters in length
        const isStrongPassword = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^])[A-Za-z\d@$!%*?&#^]{8,}$/.test(password);
        if(!isStrongPassword){
            alert('Password must include at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.');
            return;
        }
        try{
            await axios.post('http://localhost:5000/api/register', formData, {withCredentials: true});
            navigate('/login');
        } catch (err) {
            alert(err.response?.data?.error || 'Registration Failed');
            console.error(err);
        }
    };

    return (
        <div className="box">
            <HamburgerMenu />
            <br/>
            <h2>Register Now</h2>

            <input
                name="username"
                type="text"
                placeholder="Username"
                value={username}
                onChange={e => setUsername(e.target.value)}
            /><br/>
            <input
                name="password"
                type="password"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
            /><br/>
            <input
                name="first_name"
                type="text"
                placeholder="First Name"
                value={first_name}
                onChange={e => setFirstName(e.target.value)}
            /><br/>
            <input
                name="last_name"
                type="text"
                placeholder="Last Name"
                value={last_name}
                onChange={e => setLastName(e.target.value)}
            /><br /><br /><br/>

            <button className="main-button" onClick={register}>Register</button>
            <br/><br/>
        </div>
    );
}

export default Register;