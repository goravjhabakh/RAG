import { createContext, useContext } from 'react';

const UserContext = createContext("Guest");

const Welcome = () => {
  const user = useContext(UserContext);
  return <h2>Welcome, {user}!</h2>;
}

export const Gorav = () => {
  return (
    <UserContext.Provider value="Gorav">
      <Welcome />
    </UserContext.Provider>
  );
}