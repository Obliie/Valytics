import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { Text } from 'react-native-paper';

import BackButton from '../components/BackButton';
import Background from '../components/Background';
import Breaker from '../components/Breaker';
import Button from '../components/Button';
import Header from '../components/Header';
import InputField from '../components/InputField';
import Logo from '../components/Logo';
import { RegisterScreenNavigationProp } from '../helpers/NavigationTypes';
import { emailValidator } from '../helpers/emailValidator';
import { nameValidator } from '../helpers/nameValidator';
import { passwordValidator } from '../helpers/passwordValidator';
import { appStyles } from '../theme/mainStyles';
import { theme } from '../theme/theme';

interface RegisterScreenProps {
  navigation: RegisterScreenNavigationProp;
}

const RegisterScreen: React.FC<RegisterScreenProps> = ({ navigation }) => {
  const [name, setName] = useState<{ value: string; error: string }>({
    value: '',
    error: '',
  });
  const [email, setEmail] = useState<{ value: string; error: string }>({
    value: '',
    error: '',
  });
  const [password, setPassword] = useState<{ value: string; error: string }>({
    value: '',
    error: '',
  });
  const [confirmPassword, setConfirmPassword] = useState<{
    value: string;
    error: string;
  }>({
    value: '',
    error: '',
  });

  const onSignUpPressed = () => {
    // Validate name, email, and password
    const isNameValid = nameValidator(name.value, name, setName);
    const isemailValid = emailValidator(email.value, email, setEmail);
    const isPasswordValid = passwordValidator(password.value, password, setPassword);
    const isConfirmPasswordValid = passwordValidator(
      confirmPassword.value,
      confirmPassword,
      setConfirmPassword,
      password.value,
    );

    // If there are errors in name, email, or password, update the state with the error messages
    if (!isNameValid || !isemailValid || !isPasswordValid || !isConfirmPasswordValid) {
      return;
    }

    // If no errors, navigate to the Dashboard screen
    navigation.reset({
      index: 0,
      routes: [{ name: 'Dashboard', params: { email: email.value } }],
    });
  };

  const onRiotSignUpPressed = () => {
    // TO DO: Handle Riot sign up
    console.log('RIOT SIGN UP');
  };

  const onDiscordSignUpPressed = () => {
    // TO DO: Handle Discord sign up
    console.log('DISCORD SIGN UP');
  };

  return (
    <Background>
      <BackButton goBack={navigation.goBack} />

      <Logo />

      <Header>Create Account</Header>

      <InputField
        label="Name"
        returnKeyType="next"
        value={name.value}
        onChangeText={text => setName({ value: text, error: '' })}
        error={!!name.error}
        errorText={name.error}
      />
      <InputField
        label="Email"
        returnKeyType="next"
        value={email.value}
        onChangeText={text => setEmail({ value: text, error: '' })}
        error={!!email.error}
        errorText={email.error}
        autoCapitalize="none"
        autoComplete="email"
        textContentType="emailAddress"
        keyboardType="email-address"
      />
      <InputField
        label="Password"
        returnKeyType="done"
        value={password.value}
        onChangeText={text => setPassword({ value: text, error: '' })}
        error={!!password.error}
        errorText={password.error}
        secureTextEntry
      />
      <InputField
        label="Confirm Password"
        returnKeyType="done"
        value={confirmPassword.value}
        onChangeText={text => setConfirmPassword({ value: text, error: '' })}
        error={!!confirmPassword.error}
        errorText={confirmPassword.error}
        secureTextEntry
      />

      <Button mode="contained" onPress={onSignUpPressed} style={{ marginTop: 24 }}>
        <Text style={appStyles.buttonText}>Sign Up</Text>
      </Button>

      <Breaker color="grey" height={2} />

      <Button
        mode="contained"
        onPress={onRiotSignUpPressed}
        style={{ marginTop: 24 }}
        icon={require('../../assets/riot-games.png')}>
        <Text style={appStyles.buttonText}>Sign Up with Riot</Text>
      </Button>

      <Button
        mode="contained"
        onPress={onDiscordSignUpPressed}
        style={{ marginTop: 24 }}
        icon={require('../../assets/discord-logo.png')}>
        <Text style={appStyles.buttonText}>Sign Up with Discord</Text>
      </Button>

      <Breaker color="grey" height={2} />

      <View style={styles.row}>
        <Text>Already have an account? </Text>
        <TouchableOpacity onPress={() => navigation.replace('LoginScreen')}>
          <Text style={styles.link}>Login</Text>
        </TouchableOpacity>
      </View>
    </Background>
  );
};

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    marginTop: 4,
  },
  link: {
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
});

export default RegisterScreen;
