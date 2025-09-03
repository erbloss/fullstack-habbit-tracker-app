
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import 'chart.js/auto';
import { Line } from 'react-chartjs-2';

function SingleHabitGraph () {
    const [selectedHabit, setSelectedHabit] = useState('');
    const [logs, setLogs] = useState([]);
    const [habits, setHabits] = useState([]);

    // Fetch logs for a specific habit pertaining to the last 30 days
    useEffect(() => {
        const fetchLogs = async () => {
            try {
                if(selectedHabit){
                    const res = await axios.get(`http://localhost:5000/api/habits/${selectedHabit}/getlogs`, {withCredentials: true});
                    // filter to include all logs within past 30 days
                    const now = new Date();
                    const thirtyDaysAgo = new Date();
                    thirtyDaysAgo.setDate(now.getDate() - 30);

                    const filteredLogs = res.data.filter(log => {
                        const logDate = new Date(log.date);
                        return logDate>= thirtyDaysAgo && logDate <= now;
                    });
                    // ensure logs are sorted chronologically
                    filteredLogs.sort((a, b) => new Date(a.date) - new Date(b.date));
                    setLogs(filteredLogs);
                    console.log("Selected Habit = ", selectedHabit);
                }
            } catch (err) {
                console.error("Failed to fetch logs:", err);
            }
        };
        fetchLogs();
    }, [selectedHabit]);

    // Fetch all habits for user from db to populate drop down menu
    useEffect(() => {
        const fetchHabits = async () => {
            try{
                const res = await axios.get(`http://localhost:5000/api/habits`, {withCredentials: true});
                setHabits(res.data);
            } catch (err) {
                console.error("Failed to fetch habits");
            }
        };
        fetchHabits();
    }, [habits]);

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
    return (
        <div>
            <p>Select a habit to view your progress chart for the previous 30 days:</p>
            <select className="drop-down"
                id="habits"
                value={selectedHabit}
                onChange={(e) => setSelectedHabit(e.target.value)}>
                <option value="" disabled>--Select Habit--</option>
                {habits.map((habit) => (
                    <option key={habit.id} value={habit.id}>
                    {habit.name}</option>
                ))}
            </select>
            <br/><br/>
            {selectedHabit && logs.length > 0 ? (
                <Line data={chartData_single} />
                ): (
                    <div>
                    </div>
                )}
        </div>
    );
}

export default SingleHabitGraph;