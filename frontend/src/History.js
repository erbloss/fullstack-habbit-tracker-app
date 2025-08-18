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
    const [longestStreak, setLongestStreak] = useState(null);
    const [selectedHabit, setSelectedHabit] = useState('');

    // Fetch logs for a specific habit
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await axios.get(`http://localhost:5000/api/habits/${selectedHabit}/logs`, {withCredentials: true});
                setLogs(res.data);
            } catch (err) {
                console.error("Failed to fetch logs:", err);
            }
        };
        fetchLogs();
    }, [selectedHabit]);

    // Fetch logs for ALL habits
    useEffect(() => {
        const fetchAllLogs = async () => {
            try {
                const res = await axios.get(`http://localhost:5000/api/logs`, { withCredentials: true});
                setLogs(res.data);
            } catch (err) {
                console.error("Failed to fetch logs:", err);
            }
        };
        fetchAllLogs();
    }, []);

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

    // process all logs to calculate daily percentages
    const logsPercentageByDate = (logs, totalHabits) => {
        const grouped = {};
        logs.forEach(log => {
            if(!grouped[log.date]) {
                grouped[log.date] = { completed: 0, total: 0};
            }
            grouped[log.date].total += 1;
            if(log.status) {
                grouped[log.date].completed += 1;
            }
        });
        const sortedDates = Object.keys(grouped).sort((a, b) => new Date(a) - new Date(b));
        const percentages = sortedDates.map(date => ({
            date,
            percent: totalHabits > 0 ? (grouped[date].completed / totalHabits) * 100 : 0
        }));
        return percentages;
    }

    // Chart data for all habits as percentage
    const dailyPercentages = logsPercentageByDate(logs, habits.length);
    const chartData_all = {
        labels: dailyPercentages.map(item => item.date),
        datasets:[{
            label: '% Daily Habit Completion',
            date: dailyPercentages.map(item => item.percent),
            fill: false,
            borderColor: 'white',
            tension: 0.2,
        }],
    };


    // Chart data for a single habit
    const dates = logs.map(log => log.date);
    const values = logs.map(log => (log.status ? 1 : 0 ));

    const chartData_single = {
        labels: dates,
        datasets: [{
            label: 'Habit Completion',
            data: values,
            fill: false,
            borderColor: 'white',
            tension: 0.2,
        }],
    };

    // fetch streak for a single habit
    const fetchStreak = async (habitId) => {
        try{
            const res = await axios.get(`http://localhost:5000/api/habits/${habitId}/streak`, { withCredentials: true});
            return res.data.streak;
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
                    b.streak - a.streak);
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

            <p>Daily habit completion across ALL habits:</p>
            {logs.length >0? (
                <Line data={chartData_all} />
            ) : (
                <p>Loading chart data...</p>
            )}

            <p>Select a habit from the drop-down menu to view your progress chart.</p>
            <select
                id="habits"
                value={selectedHabit}
                onChange={(e) => setSelectedHabit(e.target.value)}
>
                <option value="" disabled>Habit</option>
                {habits.map((habit) => (
                    <option key={habit.id} value={habit.id}>
                        {habit.name}
                </option>
                ))}
            </select>
            {selectedHabit && logs.length > 0 ? (
                <Line data={chartData_single} />
            ): (
                <div></div>
            )}

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

            <div className="habit-streak-box">
                <h2>🏆 Your Longest Streak to Date 🏆</h2>
                {longestStreak && longestStreak > 0 ? (
                    <div><strong>{longestStreak.name}</strong> for {longestStreak.streak} consecutive days</div>
                ) : (
                    <div><strong>No records yet.  Keep working!</strong></div>
                )}
            </div>
        </div>
    );
}

export default History;
