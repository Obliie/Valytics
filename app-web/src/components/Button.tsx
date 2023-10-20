import React from 'react';
import { Image, ImageSourcePropType, StyleSheet, View } from 'react-native';
import { ButtonProps, Button as PaperButton } from 'react-native-paper';
import { theme } from '../theme/theme';

interface CustomButtonProps extends ButtonProps {
  icon?: ImageSourcePropType;
  buttonColor?: string;
}

const CustomButton: React.FC<CustomButtonProps> = ({ style, icon, buttonColor, children, ...props }) => {
  // Check if an icon is provided
  const hasIcon = !!icon;

  return (
    <PaperButton
      style={[
        styles.button,
        props.mode === 'outlined' && { backgroundColor: theme.colors.primary },
        buttonColor !== undefined && { backgroundColor: buttonColor },
        style,
      ]}
      labelStyle={styles.text}
      // Button mode (e.g., contained, outlined, etc.)
      {...props}
      // Content style for button container
      contentStyle={[
        styles.content,
        // If there's an icon, align text and icon side by side
        hasIcon && {
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'center',
        },
      ]}
      icon={({ size }) => (
        <View style={[styles.iconContainer, { width: size, height: size }]}>
          {/* Show the icon if provided */}
          {icon && <Image source={icon} style={styles.icon} />}
        </View>
      )}>
      <View style={styles.textContainer}>{children}</View>
    </PaperButton>
  );
};
const styles = StyleSheet.create({
  button: {
    width: '100%',
    marginVertical: 10,
    paddingVertical: 2,
  },
  text: {
    fontWeight: 'bold',
    fontSize: 15,
    lineHeight: 26,
  },
  textContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  icon: {
    width: 35,
    height: 35,
    resizeMode: 'contain',
  },
  content: {
    alignItems: 'center',
  },
});

CustomButton.defaultProps = {
  icon: undefined,
  buttonColor: theme.colors.primary,
};

export default CustomButton;
