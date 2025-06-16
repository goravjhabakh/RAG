import { useState } from "react";

interface PaginationProps {
    items: string[];
    itemsPerPage?: number;
}

export const Pagination = ({ items, itemsPerPage = 5 }: PaginationProps) => {
    const [curPage, setCurPage] = useState(1)
    const totalPages = Math.ceil(items.length / itemsPerPage)

    const start = (curPage - 1) * itemsPerPage
    const end = start + itemsPerPage
    const currentItems = items.slice(start,end)

    const changePage = (page: number) => {
        if (page < 1 || page > totalPages) return;
        setCurPage(page)
    }

    return (
        <div>
            <h3>Pagination: {curPage}/{totalPages}</h3>
            <ul>
                {currentItems.map((item, idx) => (
                    <li key={idx}>{item}</li>
                ))}
            </ul>
            <div>
                <button onClick={() => {changePage(curPage - 1)}}>-</button>
                <button onClick={() => {changePage(curPage + 1)}}>+</button>
            </div>
        </div>
    )
}