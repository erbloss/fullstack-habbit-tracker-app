import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import HamburgerMenu from './HamburgerMenu';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import Dashboard from './Dashboard';

function History() {
    const { habitId } = useParams();
    const [habits, setHabits] = useState([]);
    const [logs, setLogs] = useState([]);
    const [first_name, setFirstName] = useState('');
    const [currentDateTime, setCurrentDateTime] = useState(new Date());

    // Fetch logs for this habit
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await axios.get(`/api/habits/${habitId}/logs`);
                setLogs(res.data);
            } catch (err) {
                console.error("Failed to fetch logs:", err);
            }
        };
        fetchLogs();
    }, [habitId]);

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

    // Chart data
    const dates = logs.map(log => log.date);
    const values = logs.map(log => (log.status ? 1 : 0));

    const chartData = {
        labels: dates,
        datasets: [{
            label: 'Habit Completion',
            data: values,
            fill: false,
            borderColor: 'GreenYellow',
            tension: 0.2,
        }],
    };

    // fetch streak for a single habit
    const fetchStreak = async (habiId) => {
        try{
            const res = await axios.get('http://localhost:5000/api/habits/${habitId}/streak', { withCredentials: true});
            return res.data.streak;
        } catch (err) {
            console.error(`Failed to fetch streak for habit ${habitId}:`, err);
            return 0;
        }
    };

    // load all habits and their respective streaks and sort in descending order
    useEffect(() => {
        const loadHabitStreaks = async () => {
            try {
                const res = await axios.get(`http://localhost:5000/api/habits`, { withCredentials: true});
                const habitsData = res.data;
                const habitsWithStreaks = await Promise.all(habitsData.map(async habit => {
                    const streak = await fetchStreak(habit.id);
                    return { ...habit, streak};
                }));
                // sort here
                const sortedHabits = habitsWithStreaks.sort((a, b) => 
                    b.streak - a.streak);
                setHabits(sortedHabits);
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
            <p>Below is a graph of your progress.  Keep up the good work!</p>
            <Line data={chartData} />
            <br /> <br /> <br />
            <div className="habit-streak-box">
                <h2>🔥 Your Habit Hot Streaks 🔥</h2>
                {habits.map(habit => (
                    <div key={habit.id} className="habit-streaks">
                    <div><strong>{habit.name}</strong>
                        ...............Streak: {habit.streak ?? 0}</div>
                    </div>
                ))}
            </div>
            <div>
                <h2>Your Longest Streak to Date</h2>
                
            </div>
        </div>
    );
}

export default History;
