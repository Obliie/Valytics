import React from 'react';
import { StyleSheet, TextProps } from 'react-native';
import { Text } from 'react-native-paper';

import { theme } from '../theme/theme';

interface HeaderProps extends TextProps {
  // Make the children prop required
  children: React.ReactNode;
}

const Header: React.FC<HeaderProps> = ({ style, ...props }) => {
  return <Text style={[styles.header, style]} {...props} />;
};

const styles = StyleSheet.create({
  header: {
    fontSize: 25,
    color: theme.colors.primary,
    fontWeight: 'bold',
    paddingVertical: 12,
  },
});

export default Header;
