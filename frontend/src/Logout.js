import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import HamburgerMenu from './HamburgerMenu';

function Logout() {
     const navigate = useNavigate();
     const [isAuthenticated, setIsAuthenticated] = useState(null);

     useEffect(() => {
        const chechAuth = async () => {
            try {
                const res = await axios.get('http://localhost:5000/api/user', {withCredentials: true });
                setIsAuthenticated(!!res.data); //true if user data exists
            } catch (err) {
                setIsAuthenticated(false);
            }
        };
        chechAuth();
     }, []);
     

 
     const handleLogout = async () => {
        try {
            await axios.post('http://localhost:5000/api/logout', {}, { withCredentials: true});
            navigate('/login');
        } catch (err) {
            alert('Logout Failed', err);
        }
    };
    const handleGoBack = () => {
        if (isAuthenticated === false) {
            navigate('/login');
        } else {
            navigate(-1); // goes back one page
        }
    };

    // message if in loading state
    if (isAuthenticated === null) return <p>Checking authentication...</p>;
    
    return (
        <div className="box">
            <HamburgerMenu />
            <br />
            <h2>Sign Out</h2>
            <p>Are you ready to go?</p>
            <div className="button-group">
                <button onClick={handleLogout}>Yes, Sign Out</button>
                <button onClick={handleGoBack}>No, Go Back</button>
            </div>
            <br />
        </div>
    );
};

export default Logout;
