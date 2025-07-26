import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import HamburgerMenu from './HamburgerMenu';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';
import Dashboard from './Dashboard';

function History() {
    const { habitId } = useParams();
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

    return (
        <div className="box">
            <HamburgerMenu />
            <h4>{currentDateTime.toLocaleString()}</h4>
            <h3>Track your progress, {first_name}!</h3>
            <h2>🌱 Completeness History 🌱</h2>
            <p>Below is a graph of your progress.  Keep up the good work!</p>
            <Line data={chartData} />
        </div>

    );
}

export default History;
