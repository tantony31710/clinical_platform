import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import { login as apiLogin, logout as apiLogout } from '../lib/api';
import type { LoginPayload, AuthUser } from '../types';

// ─── Types ─────────────────────────────────────────────────────────────────
interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
}

// ─── Context ───────────────────────────────────────────────────────────────
const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ──────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    // Restore user from sessionStorage on page refresh
    const stored = sessionStorage.getItem('clinical_user');
    return stored ? (JSON.parse(stored) as AuthUser) : null;
  });
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (payload: LoginPayload) => {
    setIsLoading(true);
    try {
      await apiLogin(payload);
      const newUser: AuthUser = { patient_id: payload.patient_id };
      setUser(newUser);
      sessionStorage.setItem('clinical_user', JSON.stringify(newUser));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiLogout();
    } catch {
      // Always clear client state even if server call fails
    } finally {
      setUser(null);
      sessionStorage.removeItem('clinical_user');
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: user !== null,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ──────────────────────────────────────────────────────────────────
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}

export default AuthContext;
