import React, { createContext, useContext, useState, useEffect } from 'react';

export type Theme = 'dark' | 'cyber' | 'light';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    try {
      const stored = localStorage.getItem('productiq_theme') as Theme;
      if (stored && ['dark', 'cyber', 'light'].includes(stored)) {
        return stored;
      }
    } catch {
      // fallback
    }
    return 'dark';
  });

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-dark', 'theme-cyber', 'theme-light', 'dark', 'light');

    if (theme === 'cyber') {
      root.classList.add('theme-cyber', 'dark');
    } else if (theme === 'light') {
      root.classList.add('theme-light', 'light');
    } else {
      root.classList.add('theme-dark', 'dark');
    }

    try {
      localStorage.setItem('productiq_theme', theme);
    } catch {
      // ignore
    }
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
