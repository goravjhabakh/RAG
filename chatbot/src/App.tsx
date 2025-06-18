import {ChatArea} from "./components/ChatArea";

export const App = () => {
  const userId = '1';

  return (
    <div>
      <ChatArea userId={userId}/>
    </div>
  )
}