import { useEffect, useState } from "react";

type ChatMessage = {role: 'user' | 'ai'; text: string}
type historyItem = {user?: string, ai?: string}

export const useChat = (userId: string) => {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [loading, setLoading] = useState(true)

    const loadHistory = async () => {
        try {
            const res = await fetch(`http://127.0.0.1:8000/rag/get-all-chats/${userId}`)
            const data = await res.json()

            console.log(data.history)

            setMessages(data.history.map((item: historyItem) => {
                if (item.user) return {role: 'user', text: item.user}
                if (item.ai) return {role: 'ai', text: item.ai};
                return null;
            }).filter(Boolean) as ChatMessage[]
        )
        } catch (err) {
            console.error(`Error loading chat history: ${err}`)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {loadHistory()},[userId])
    return {messages, loading, setMessages};
}