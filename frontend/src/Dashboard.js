import React, { useEffect, useState } from 'react';
import { Fragment } from 'react';
import axios from 'axios';
import HamburgerMenu from './HamburgerMenu';

function Dashboard() {
    const [habits, setHabits] = useState([]);
    const [newHabit, setNewHabit] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const categories = ["Fitness", "Wellness", "Work", "Household", "Relationship", "Other"];
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

    // ********  HABITS ******************************************
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
        await axios.post('http://localhost:5000/api/habits', { name: newHabit, category: selectedCategory}, { withCredentials: true});
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

    // update the habit category
    const updateHabitCategory = async (id, newCategory) => {
        try {
            await axios.put(`http://localhost:5000/api/habits/${id}`,
            { category: newCategory }, { withCredentials: true });
            fetchHabits(); // Refresh the habits after update
        } catch (err) {
            console.error("Failed to update category:", err);
        }
    };

    // handle the toggle action so that the db is updated for status
    const handleToggle = async (habitId, isChecked) => {
        const today = new Date().toLocaleDateString('en-CA');
        console.log(today);
        
        try {
            const response = await fetch(`http://localhost:5000/api/habits/${habitId}/log`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                credentials: 'include',
                body: JSON.stringify({
                    date: today, 
                    status: isChecked,
                }),
            });
            const result = await response.json();
            console.log(result.message || result.error);

            setHabits(prevHabits =>
                prevHabits.map( habit =>
                    habit.id === habitId ? { ...habit, completed: isChecked }
                    : habit
                )
            );
        } catch (err) {
            console.error('Toggle update failed: ', err);
        }
    };

    // ********** UI *****************************
    return (
        <div className="box">
            <HamburgerMenu />
            <h4>{currentDateTime.toLocaleString()}</h4>
            <h3>Welcome, {first_name}!</h3>
            <h2>📋 Your Daily Habits 📋</h2>
            <p>Add any daily habit that you would like to track using the input field below:</p>

            <input value={newHabit} onChange={e => setNewHabit(e.target.value)} placeholder=" New Habit" />

            <select
                id="categories"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
>
                <option value="" disabled>Category</option>
                {categories.map((category, index) => (
                    <option key={index} value={category}>
                        {category}
                </option>
                ))}
            </select>
            <button onClick={addHabit}>Add</button>
            <p className="small-text">(e.g., "Exercise", "Drink 10 cups of water", "Read for 30 min")</p>

            <div className="habit-grid">
                <div className="grid-header">Habit</div>
                <div className="grid-header">Category</div>
                <div className="grid-header">Status</div>
                <div className="grid-header">Delete</div>

                {habits.map(habit => (
                    <React.Fragment key={habit.id}>
                        <div 
                            className="habit-text"
                            data-fulltext={habit.name}
                            title={habit.name}>
                                {habit.name}</div>

                        <div 
                            className="habit-text"
                            data-fulltext={habit.category} 
                            title={habit.category}>
                                {habit.category}</div>

                        <div className="toggle-switch" >
                            <input 
                                type="checkbox" 
                                id={`toggle-${habit.id}`}
                                checked={habit.completed} 
                                onChange={(e) => handleToggle(habit.id, e.target.checked)} />
                            <label htmlFor={`toggle-${habit.id}`}></label></div>

                        <div><button onClick={() => deleteHabit(habit.id)} className="trash-button">🗑️</button></div>  

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