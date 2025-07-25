import React, { useEffect, useState } from 'react';
import { Fragment } from 'react';
import axios from 'axios';

function Dashboard() {
    const [habits, setHabits] = useState([]);
    const [newHabit, setNewHabit] = useState('');

    useEffect(() => {
        fetchHabits();
    }, []);

    //refresh the habits list
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

    const markUndone = async (id) => {
        await axios.post(`http://localhost:5000/api/habits/${id}/undo`, {}, { withCredentials: true });
        fetchHabits();
    };


    const deleteHabit = async (id) => {
        const confirmDelete = window.confirm("Are you sure you want to delete this habit?");
        if (!confirmDelete) return;

        try {
            await axios.delete(`http://localhost:5000/api/habits/${id}`, { withCredentials: true });
            fetchHabits(); // Refresh the list after deletion
        } catch (err) {
            console.error("Failed to delete habit:", err);
        }
    };


    const resetHabits = async () => {
        await axios.post(`http://localhost:5000/api/habits/reset`, {}, { withCredentials: true });
        fetchHabits();
    };

    const clearHabits = async () => {
        const confirmDelete = window.confirm("Are you sure you want to clear all habits?");
        if (!confirmDelete) return;

        try {
            await axios.post(`http://localhost:5000/api/habits/reset`, {}, { withCredentials: true });
            setHabits([]);
        }catch (err){
            console.error("Failed to clear habits", err);
        }
    };

    const logout = async () => {
        await axios.post('http://localhost:5000/api/logout', {}, { withCredentials: true });
        window.location.href = '/login';
    };

    return (
        <div className="box">
            <h2>Your Habits</h2>

            <input value={newHabit} onChange={e => setNewHabit(e.target.value)} placeholder="New Habit" />
            <button onClick={addHabit}>Add</button>
            <p className="small-text">(e.g., "Exercise", "Drink 10 cups of water", "Read for 30 min")</p>

            <div className="habit_grid">
                <div className="grid-header">Habit</div>
                <div className="grid-header">Status</div>
                <div className="grid-header">Action</div>
                <div className="grid-header">Delete</div>

                {habits.map(habit => (
                    <React.Fragment key={habit.id}>
                        <div>{habit.name}</div>
                        <div>{habit.completed ? '✅' : '❌'}</div>
                        <div>{habit.completed ? (
                            <button onClick={() => markUndone(habit.id)}>Mark Undone</button>
                            ) : (
                            <button onClick={() => markDone(habit.id)}>Mark Done</button>
                            )}
                        </div>
                        <div><button onClick={() => deleteHabit(habit.id)} className="delete-button">🗑️</button>
                        </div>
                    </React.Fragment>
                ))}

            </div>

            {habits.length > 0 && habits.every(habit => habit.completed) && (
                <p className="congrats-msg">CONGRATULATIONS! You've completed all of your daily habits!</p>
            )}

            <div className="button-group">
                <button onClick={resetHabits}>Reset</button>
                <button onClick={clearHabits}>Clear All</button>
                <button onClick={logout}>Logout</button>
            </div>
        </div>
    );
}

export default Dashboard;