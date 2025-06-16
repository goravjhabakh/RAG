// Whenever lap changes the component re-renders and useEffect
// is called to reset the time and it depends on lap variable

import { useState, useEffect } from "react";

export const LapTimer = () => {
    const [seconds, setSeconds] = useState(0)
    const [lap, setLap] = useState(0)

    useEffect(() => {
        const interval = setInterval(() => {
            setSeconds((s) => s + 1)
        }, 1000)

        return () => clearInterval(interval)
    }, [lap])

    const handleLap = () => {
        setLap(lap + 1)
        setSeconds(0)
    }

    return (
        <div>
            <h2>Timer: {seconds}    Laps: {lap}</h2>
            <button onClick={handleLap}>Lap</button>
        </div>
    )
}