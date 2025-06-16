import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
//import { Gorav } from './hooks/useContext'
//import { UseMemo } from './hooks/useMemo'
//import { Pagination } from './hooks/Pagination'
import { App } from './App.tsx'

//const sampleItems = Array.from({ length: 23 }, (_, i) => `Item ${i + 1}`);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App/>
  </StrictMode>,
)
