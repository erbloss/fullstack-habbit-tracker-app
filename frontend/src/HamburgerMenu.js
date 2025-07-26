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
                    <Link to="/" onClick={() => setOpen(false)}>My Habits</Link>
                    <Link to="/history" onClick={() => setOpen(false)}>My Progress</Link>
                    <Link to="/register" onClick={() => setOpen(false)}>Sign Up</Link>
                    <Link to="/login" onClick={() => setOpen(false)}>Sign in</Link>
                    <Link to="/logout" onClick={() => setOpen(false)}>Sign Out</Link>
                </div>
            )}
        </div>
    );
}

export default HamburgerMenu;