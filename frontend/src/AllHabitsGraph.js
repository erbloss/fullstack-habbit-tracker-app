import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

function AllHabitsGraph() {
    const [logs, setLogs] = useState([]);
    const [habits, setHabits] = useState([]);
    var percentages = [];

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


    // Fetch logs for ALL habits
    useEffect(() => {
        const fetchAllLogs = async () => {
            try {
                const res = await axios.get(`http://localhost:5000/api/habits/getlogs`, { withCredentials: true});
                setLogs(res.data);
            } catch (err) {
                console.error("Failed to fetch logs:", err);
            }
        };
        fetchAllLogs();
    }, [logs]);

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
        percentages = sortedDates.map(date => ({
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

    return (
        <div>
            <p>Daily habit completion across ALL habits:</p>
                {logs.length > 0 ? (
                    <Line data={chartData_all} />
                ) : (
                    <p>Loading chart data...</p>
                )}
        </div>
    )
}

export default AllHabitsGraph;