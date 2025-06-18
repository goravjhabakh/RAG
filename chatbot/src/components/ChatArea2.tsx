import { useState, useEffect, useRef} from 'react';
import '../index.css';
import { useChat } from "../hooks/useChat";
import { endpoints } from '@/config';
//import {FaUser, FaRobot} from 'react-icons/fa'

interface ChatAreaProps {
  userId: string;
}

export const ChatArea = ({userId}: ChatAreaProps) => {
    const {messages, loading, setMessages} = useChat(userId);
    const [input, setInput] = useState('')
    const [sending, setSending] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement | null>(null);

    const scrollToBottom = () => {messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });};
    useEffect(() => {scrollToBottom();}, [messages]);


    const handleSend = async() => {
        if (!input.trim()) return;
        setMessages((prev) => [...prev, {role: 'user', text: input.trim()}])
        setInput('')
        setSending(true)

        try {
            console.log(JSON.stringify({query: input.trim(), user_id: parseInt(userId)}))

            const res = await fetch(endpoints.query, {
                method: 'POST',
                headers: {"Content-Type": "application/json",},
                body: JSON.stringify({query: input.trim(), user_id: parseInt(userId)})
            })
            const data = await res.json()

            if (data.success) {
                setMessages((prev) => [...prev, {role: 'ai', text: data.answer}])
            } else {
                setMessages((prev) => [...prev, {role: 'ai', text: 'Failed to get response'}])
            }
        } catch (err) {
            console.error(`Error: ${err}`)
            setMessages((prev) => [...prev, {role: 'ai', text: 'Error processing your query!'}])
        } finally {
            setSending(false)
        }
    }

    return (
        <div>
            <div className="chat-container">
                <div className="chat-header">ChatBot</div>
                <div className="chat-messages">
                    {loading ? (
                    <p className="chat-status">Loading chat history...</p>
                    ) : messages.length === 0 ? (
                    <p className="chat-status">No chat history found.</p>
                    ) : (
                    messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                        {msg.text}
                        </div>
                    ))
                    )}
                    <div ref={messagesEndRef} />
                </div>
                <div className="chat-input-area">
                    <input 
                    type="text" 
                    className="chat-input" 
                    placeholder='Search..'
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    />
                    <button className="chat-send-button" onClick={handleSend}>
                        {sending ? '...' : 'Send'}
                    </button>
                </div>
            </div>
        </div>
    )
}