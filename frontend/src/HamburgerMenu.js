import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './HamburgerMenu.css';

function HamburgerMenu() {
    const [open, setOpen] = useState(false);

    return (
        <div className="hamburger-wrapper">
            <button className="hamburger-button" onClick={() => setOpen(!open)}>
             ☰
            </button>

            {open && (
                <div className={`menu-dropdown ${open ? 'open' : 'closed'}`}>
                    <Link to="/" onClick={() => setOpen(false)}>Dashboard</Link>
                    <Link to="/login" onClick={() => setOpen(false)}>Login</Link>
                    <Link to="/register" onClick={() => setOpen(false)}>Register</Link>
                </div>
            )}
        </div>
    );
}

export default HamburgerMenu;