import React, { useEffect, useState } from 'react';
import axios from 'axios';
import HamburgerMenu from './HamburgerMenu';
import SingleHabitGraph from './SingleHabitGraph';
import AllHabitsGraph from './AllHabitsGraph';
import 'chart.js/auto';

function History() {
    const [habits, setHabits] = useState([]);
    const [first_name, setFirstName] = useState('');
    const [currentDateTime, setCurrentDateTime] = useState(new Date());
    const [longestStreak, setLongestStreak] = useState(null);

    // Get current user first name and update clock
    useEffect(() => {
        const fetchFirstName = async () => {
            try {
                const res = await axios.get('http://localhost:5000/api/user', { withCredentials: true });
                setFirstName(res.data.first_name);
            } catch (err) {
                console.error("Failed to fetch user info:", err);
            }
        };
        fetchFirstName();

        const timer = setInterval(() => {
            setCurrentDateTime(new Date());
        }, 1000);

        return () => clearInterval(timer); // cleanup
    }, []);


    // fetch streak for a single habit
    const fetchStreak = async (habitId) => {
        try{
            const res = await axios.get(`http://localhost:5000/api/habits/${habitId}/streak`, { withCredentials: true});
            return Number(res.data.streak);
        } catch (err) {
            console.error(`Failed to fetch streak for habit ${habitId}:`, err);
            return 0;
        }
    };

    // load all habits and their respective streaks
    useEffect(() => {
        const loadHabitStreaks = async () => {
            try {
                const res = await axios.get(`http://localhost:5000/api/habits`, { withCredentials: true});

                const habitsData = res.data;
                const habitsWithStreaks = await Promise.all(habitsData.map    (async habit => {
                    const streak = await fetchStreak(habit.id);
                    return { ...habit, streak};
                }));
                // sort here
                const sortedHabits = habitsWithStreaks.sort((a, b) => 
                    (b.streak ?? 0) - (a.streak ?? 0));
                setHabits(sortedHabits);
                // find the longest streak
                const longest = sortedHabits.length > 0 ? sortedHabits[0] : null;
                setLongestStreak(longest);
            } catch (err) {
                console.error("Failed to fetch habits:", err);
            }
        };
        loadHabitStreaks();
    }, []);

    return (
        <div className="box">
            <HamburgerMenu />
            <h4>{currentDateTime.toLocaleString()}</h4>

            <h3>Track your progress, {first_name}!</h3>
            <h2>🌱 Completeness History 🌱</h2>

            <AllHabitsGraph />
            <br /> <br /> <br/>

            

            <div className="habit-streak-box">
                <h2>🔥 Your Current Hot Streaks 🔥</h2>
                {habits.map(habit => (
                    <div key={habit.id} className="habit-streaks">
                    <div><strong>{habit.name}</strong>
                        ...............Streak: {habit.streak}</div>
                    </div>
                ))}
            </div>
            <br /> <br /> <br />
            
            <SingleHabitGraph />
            <br /> <br /> <br />
        </div>
    );
}

export default History;
