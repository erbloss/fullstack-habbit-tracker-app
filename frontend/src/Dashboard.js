import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard() {
    const [habits, setHabits] = useState([]);
    const [newHabit, setNewHabit] = useState('');

    useEffect(() => {
        fetchHabits();
    }, []);

    const fetchHabits = async () => {
        try{
            const res = await axios.get('http://localhost:5000/api/habits', { withCredentials: true });
            setHabits(res.data);
        } catch (err) {
            window.location.href = '/login';
        }
    };

    const addHabit = async () => {
        await axios.post('http://localhost:5000/api/habits', { name: newHabit }, { withCredentials: true});
        setNewHabit('');
        fetchHabits();
    };

    const markDone = async (id) => {
        await axios.post(`http://localhost:5000/api/habits/${id}/complete`, {}, { withCredentials: true });
        fetchHabits();
    };

    const resetHabits = async () => {
        await axios.post(`http://localhost:5000/api/habits/reset`, {}, { withCredentials: true });
        fetchHabits();
    };

    const logout = async () => {
        await axios.post('http://localhost:5000/api/logout', {}, { withCredentials: true });
        window.location.href = '/login';
    };

    return (
        <div>
            <h2>Your Habits</h2>
            <input value={newHabit} onChange={e => setNewHabit(e.target.value)} placeholder="New Habit" />
            <button onClick={addHabit}>Add</button>
            <ul>
                {habits.map(h => (
                    <li key={h.id}>
                        {h.name} - {h.completed? '✅' : '❌' }
                        {!h.completed && <button onClick={() => markDone(h.id)}>Mark Done</button>}
                    </li>
                ))}
            </ul>

            <button onClick={resetHabits}>Reset</button><br />

            <button onClick={logout}>Logout</button>
        </div>
    );
}

export default Dashboard;