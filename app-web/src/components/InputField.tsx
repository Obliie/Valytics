import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { TextInput as Input } from 'react-native-paper';

import { theme } from '../theme/theme';

interface InputFieldProps {
  errorText?: string;
  description?: string;
}

const InputField: React.FC<
  InputFieldProps & React.ComponentProps<typeof Input>
> = ({ errorText, description, ...props }) => {
  return (
    <View style={styles.container}>
      <Input
        style={styles.input}
        selectionColor={theme.colors.primary}
        underlineColor="transparent"
        mode="outlined"
        {...props}
      />
      {description && !errorText ? (
        <Text style={styles.description}>{description}</Text>
      ) : null}
      {errorText ? <Text style={styles.error}>{errorText}</Text> : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    marginVertical: 12,
  },
  input: {
    backgroundColor: theme.colors.surface,
  },
  description: {
    fontSize: 13,
    color: theme.colors.secondary,
    paddingTop: 8,
  },
  error: {
    fontSize: 13,
    color: theme.colors.error,
    paddingTop: 8,
  },
});

export default InputField;
