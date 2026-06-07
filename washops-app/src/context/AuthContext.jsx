import { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChange, signIn, signOut } from '../lib/db';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(undefined);

  useEffect(() => {
    return onAuthStateChange(setSession);
  }, []);

  return (
    <AuthContext.Provider value={{ session, loading: session === undefined, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
