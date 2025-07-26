import React, { useEffect, useState } from 'react';
import { Fragment } from 'react';
import axios from 'axios';
import HamburgerMenu from './HamburgerMenu';

function Dashboard() {
    const [habits, setHabits] = useState([]);
    const [newHabit, setNewHabit] = useState('');
    const [first_name, setFirstName] = useState('');
    const [currentDateTime, setCurrentDateTime] = useState(new Date());

    useEffect(() => {
        fetchHabits();
        fetchFirstName();
        const timer = setInterval(() => {
            setCurrentDateTime(new Date());
        }, 1000);

        return () => clearInterval(timer); // cleanup
    }, []);

    //get current username
    const fetchFirstName = async () => {
        try {
            const res = await axios.get('http://localhost:5000/api/user', { withCredentials: true});
            setFirstName(res.data.first_name);
        } catch (err) {
            console.error("Failed to getch user info:", err);
        }
    };

    //refresh the habits list
    const fetchHabits = async () => {
        try{
            const res = await axios.get('http://localhost:5000/api/habits', { withCredentials: true });
            setHabits(res.data);
        } catch (err) {
            window.location.href = '/login';
        }
    };

    // add a new habit
    const addHabit = async () => {
        await axios.post('http://localhost:5000/api/habits', { name: newHabit }, { withCredentials: true});
        setNewHabit('');
        fetchHabits();
    };

    // mark habit as done
    const markDone = async (id) => {
        await axios.post(`http://localhost:5000/api/habits/${id}/complete`, {}, { withCredentials: true });
        fetchHabits();
    };

    // mark habit as not done
    const markUndone = async (id) => {
        await axios.post(`http://localhost:5000/api/habits/${id}/undo`, {}, { withCredentials: true });
        fetchHabits();
    };

    // remove a single specific habit
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

    // undo complete status of all habits
    const resetHabits = async () => {
        await axios.post(`http://localhost:5000/api/habits/reset`, {}, { withCredentials: true });
        fetchHabits();
    };

    // remove all habits from list
    const clearHabits = async () => {
        const confirmDelete = window.confirm("Are you sure you want to clear all habits?");
        if (!confirmDelete) 
            return;
        try {
            await axios.post(`http://localhost:5000/api/habits/reset`, {}, { withCredentials: true });
            setHabits([]);
        }catch (err){
            console.error("Failed to clear habits", err);
        }
    };

    return (
        <div className="box">
            <HamburgerMenu />
            <h4>{currentDateTime.toLocaleString()}</h4>
            <h3>Welcome, {first_name}!</h3>
            <h2>📋 Your Daily Habits 📋</h2>
            <p>Add any daily habit that you would like to track using the input field below:</p>

            <input value={newHabit} onChange={e => setNewHabit(e.target.value)} placeholder="New Habit" />
            <button onClick={addHabit}>Add</button>
            <p className="small-text">(e.g., "Exercise", "Drink 10 cups of water", "Read for 30 min")</p>

            <div className="habit-grid">
                <div className="grid-header">Habit</div>
                <div className="grid-header">Status</div>
                <div className="grid-header">Action</div>
                <div className="grid-header">Delete</div>

                {habits.map(habit => (
                    <React.Fragment key={habit.id}>
                        <div 
                            className="habit-name"
                            data-fulltext={habit.name}
                            title={habit.name}>
                                {habit.name}</div>
                        <div >{habit.completed ? '✅' : '❌'}</div>
                        <div >{habit.completed ? (
                            <button onClick={() => markUndone(habit.id)}>Unheck</button>
                            ) : (
                            <button onClick={() => markDone(habit.id)}
                            >Check</button>
                            )}
                        </div>
                        <div><button onClick={() => deleteHabit(habit.id)} className="trash-button">🗑️</button>
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
            </div>
        </div>
    );
}

export default Dashboard;