import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, name?: string, role?: User['role']) => void;
  loginWithGoogle: () => void;
  loginAsDemo: (preset: 'pm' | 'engineer') => void;
  updateProfile: (updatedData: Partial<User>) => void;
  logout: () => void;
}

const DEFAULT_USER: User = {
  id: 'usr_pm_101',
  name: 'Alex Vance',
  email: 'alex.vance@productiq.ai',
  role: 'Product Manager',
  avatar: 'AV',
};

const DEMO_PRESETS: Record<'pm' | 'engineer', User> = {
  pm: {
    id: 'usr_pm_101',
    name: 'Alex Vance',
    email: 'alex.vance@productiq.ai',
    role: 'Product Manager',
    avatar: 'AV',
  },
  engineer: {
    id: 'usr_eng_202',
    name: 'Sarah Connor',
    email: 'sarah.c@productiq.ai',
    role: 'Lead Engineer',
    avatar: 'SC',
  },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem('productiq_user');
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      // fallback
    }
    return DEFAULT_USER;
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem('productiq_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('productiq_user');
    }
  }, [user]);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const login = (email: string, name?: string, role?: User['role']) => {
    const formattedName = name?.trim() || email.split('@')[0].replace('.', ' ') || 'ProductIQ User';
    const initials = getInitials(formattedName);

    const newUser: User = {
      id: `usr_${Date.now()}`,
      name: formattedName,
      email: email.trim(),
      role: role || 'Product Manager',
      avatar: initials,
    };
    setUser(newUser);
  };

  const loginWithGoogle = () => {
    const googleUser: User = {
      id: `usr_g_${Date.now()}`,
      name: 'Alex Google',
      email: 'alex.google@productiq.ai',
      role: 'Product Manager',
      avatar: 'AG',
    };
    setUser(googleUser);
  };

  const loginAsDemo = (preset: 'pm' | 'engineer') => {
    setUser(DEMO_PRESETS[preset]);
  };

  const updateProfile = (updatedData: Partial<User>) => {
    setUser((prev) => {
      if (!prev) return null;
      const newName = updatedData.name || prev.name;
      return {
        ...prev,
        ...updatedData,
        avatar: getInitials(newName),
      };
    });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        loginWithGoogle,
        loginAsDemo,
        updateProfile,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
