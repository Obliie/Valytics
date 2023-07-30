import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';
import { Text } from 'react-native-paper';

import Background from '../components/Background';
import Breaker from '../components/Breaker';
import Button from '../components/Button';
import Header from '../components/Header';
import InputField from '../components/InputField';
import Logo from '../components/Logo';
import { emailValidator } from '../helpers/emailValidator';
import { passwordValidator } from '../helpers/passwordValidator';
import { appStyles } from '../theme/mainStyles';
import { theme } from '../theme/theme';

interface LoginScreenProps {
  navigation: any;
}

export default function LoginScreen({ navigation }: LoginScreenProps) {
  const [email, setEmail] = useState<{ value: string; error: string }>({
    value: '',
    error: '',
  });
  const [password, setPassword] = useState<{ value: string; error: string }>({
    value: '',
    error: '',
  });

  const onLoginPressed = () => {
    // Validate email and password
    const isEmailValid = emailValidator(email.value, email, setEmail);
    const isPasswordValid = passwordValidator(password.value, password, setPassword);

    // If there are errors in email or password, return early
    if (!isEmailValid || !isPasswordValid) {
      return;
    }

    // If no errors, navigate to the Dashboard screen and pass the entered email as prop for testing
    navigation.reset({
      index: 0,
      routes: [{ name: 'Dashboard', params: { email: email.value } }],
    });
  };

  const onRiotLoginPressed = () => {
    // TO DO: Handle Riot login
    console.log('RIOT LOGIN');
  };

  const onDiscordLoginPressed = () => {
    // TO DO: Handle Discord login
    console.log('DISCORD LOGIN');
  };

  return (
    <Background>
      <Logo />
      <Header>Login</Header>

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

      <View style={styles.forgotPassword}>
        <TouchableOpacity onPress={() => navigation.navigate('ResetPasswordScreen')}>
          <Text style={styles.forgot}>Forgot your password?</Text>
        </TouchableOpacity>
      </View>

      <Button mode="contained" onPress={onLoginPressed}>
        <Text style={appStyles.buttonText}>Login</Text>
      </Button>

      <Breaker color="grey" height={2} />

      <Button mode="contained" onPress={onRiotLoginPressed} icon={require('../../assets/riot-games.png')}>
        <Text style={appStyles.buttonText}>Login with Riot</Text>
      </Button>

      <Button mode="contained" onPress={onDiscordLoginPressed} icon={require('../../assets/discord-logo.png')}>
        <Text style={appStyles.buttonText}>Login with Discord</Text>
      </Button>

      <Breaker color="grey" height={2} />

      <View style={styles.row}>
        <Text>Don't have an account? </Text>
        <TouchableOpacity onPress={() => navigation.replace('RegisterScreen')}>
          <Text style={styles.link}>Sign up</Text>
        </TouchableOpacity>
      </View>
    </Background>
  );
}

const styles = StyleSheet.create({
  forgotPassword: {
    width: '100%',
    alignItems: 'flex-end',
    marginBottom: 24,
  },
  row: {
    flexDirection: 'row',
    marginTop: 4,
  },
  forgot: {
    fontSize: 13,
    color: theme.colors.secondary,
  },
  link: {
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
});
