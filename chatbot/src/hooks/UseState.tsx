// Updates the character count in text area, so everytime any character is added,
// deleted or modified it will update the character count state

import { useState } from "react";

export const CharCounter = () => {
    const [text, setText] = useState("");

    return (
        <div>
            <h3>Character Counter</h3>
            <textarea value={text} onChange={(e) => {setText(e.target.value)}} placeholder="Enter text..."/>
            <p>Character Count: {text.length}</p>
        </div>
    )
}