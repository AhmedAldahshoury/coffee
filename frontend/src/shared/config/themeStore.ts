import { create } from 'zustand';

interface ThemeState {
  darkMode: boolean;
  toggle: () => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  darkMode: true,
  toggle: () => set((state) => ({ darkMode: !state.darkMode })),
}));
