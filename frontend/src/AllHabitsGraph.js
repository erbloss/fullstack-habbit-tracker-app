import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

function AllHabitsGraph() {
    const [userId, setUserId] = useState('');
    const [completionData, setCompletionData] = useState([]);
    const [loading, setLoading] = useState([]);

    //get current user id
    const fetchUserId = async () => {
        try {
            const res = await axios.get('http://localhost:5000/api/user', { withCredentials: true});
            setUserId(res.data.id);
        } catch (err) {
            console.error("Failed to fetch user info:", err);
        }
    };

    // fetch completion % rates by day for the user
    useEffect(() => {
        fetchUserId();
        axios.get(`/api/completion_history/${userId}`, { withCredentials: true })
            .then(res => {
                setCompletionData(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error loading completion history", err);
                setLoading(false);
            });
    }, [userId]);

    // fill line chart
    const chartData = {
        labels: completionData.map(item => item.date),
        datasets: [{
            label: '% Daily Habit Completion',
            data: completionData.map(item => item.completion_rate),
            fill: false,
            borderColor: 'white',
            backgroundColor: 'white',
            tension: 0.2,
        }],
    };

    return (
        <div>
            <p>Daily habit completion across ALL habits:</p>
                {loading ? (
                    <p>Loading chart data...</p>
                ) : (
                    <Line data={chartData} />
                )}
        </div>
    )
}

export default AllHabitsGraph;