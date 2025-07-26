import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import HamburgerMenu from './HamburgerMenu';

function Login() {
    const [username, setUserName] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const login = async () => {
        try {
            await axios.post('http://localhost:5000/api/login', { username, password }, { withCredentials: true});
            navigate('/');
        } catch (err) {
            alert('Login Failed');
        }
    };
    return (
        <div className="box">
            <HamburgerMenu />
            <br />
            <h2>Login</h2>
            <input placeholder="Username" value={username} onChange={e => setUserName(e.target.value)} /><br />
            <input placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} /><br /><br />
            <button className="main-button" onClick={login}>Login</button>
            <ul>New user? Please click <Link to="/register"> here</Link> to register as a new user.</ul>
            <br />
        </div>
    );
}

export default Login;