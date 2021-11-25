import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855-lab6a.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Air Pressure</th>
							<th>Temperature</th>
						</tr>
						<tr>
							<td># Air-Pressure: {stats['num_ap_readings']}</td>
							<td># Temperature: {stats['num_temp_readings']}</td>
						</tr>
						<tr>
							<td colspan="2">Max low temp: {stats['max_temp_low_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max intermediate temp: {stats['max_temp_intermediate_reading']}</td>
						</tr>
                        <tr>
							<td colspan="2">Max high temp: {stats['max_temp_high_reading']}</td>
						</tr>
                        <tr>
							<td colspan="2">Max intermediate temp: {stats['max_bp_dia_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Max AP: {stats['max_ap_reading']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
