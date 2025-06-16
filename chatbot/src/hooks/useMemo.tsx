// count function called only when nums are updated 
// Nothing happens when the input box is updated

import { useMemo, useState } from "react";

export const UseMemo = () => {
    const [nums, setNums] = useState<number[]>([1,2,3,4,5])
    const [text, setText] = useState('')

    const count = useMemo(() => {
        console.log('Count function')
        return nums.filter((n) => n % 2 === 0).length
    }, [nums])

    return (
        <div>
            <h3>Even Numbers Count: {count}</h3>
            <button onClick={() => setNums([...nums, nums.length+1])}>Add Number</button>
            <input type="text" value={text} onChange={(e) => setText(e.target.value)}/>
        </div>
    )
}