import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Register() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const register = async () => {
        try{
            await axios.post('http://localhost:5000/api/register', { username, password }, {withCredentials: true});
            navigate('/login');
        } catch (err) {
            alert('Registration Failed');
        }
    };

    return (
        <div>
            <h2>Register Now</h2>
            <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} /><br />
            <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} /><br />
            <button onClick={register}>Register</button>
        </div>
    );
}

export default Register;