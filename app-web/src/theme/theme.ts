import { MD3DarkTheme } from 'react-native-paper';

export const theme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    // Customize the colors for dark mode here
    primary: '#FFA500', // Orange
    secondary: '#FF1493', // Deep Pink
    accent: '#00BFFF', // Deep Sky Blue
  },
};
