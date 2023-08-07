import React, { useState } from 'react';
import { Text } from 'react-native-paper';

import BackButton from '../components/BackButton';
import Background from '../components/Background';
import Breaker from '../components/Breaker';
import Button from '../components/Button';
import Header from '../components/Header';
import InputField from '../components/InputField';
import Logo from '../components/Logo';
import { emailValidator } from '../helpers/emailValidator';
import { appStyles } from '../theme/mainStyles';

interface ResetPasswordScreenProps {
  navigation: any;
}

const ResetPasswordScreen: React.FC<ResetPasswordScreenProps> = ({ navigation }) => {
  const [email, setEmail] = useState<{ value: string; error: string }>({
    value: '',
    error: '',
  });

  // Function to handle sending the reset password email
  const sendResetPasswordEmail = () => {
    const isEmailValid = emailValidator(email.value, email, setEmail);

    // If there's an error with the email, update the state with the error message
    if (!isEmailValid) {
      return;
    }

    // If the email is valid, navigate to the LoginScreen
    backToLogin();
  };

  const backToLogin = () => {
    navigation.navigate('LoginScreen');
  };

  return (
    <Background>
      <BackButton goBack={navigation.goBack} />

      <Logo />

      <Header>Restore Password</Header>

      <InputField
        label="E-mail address"
        returnKeyType="done"
        value={email.value}
        onChangeText={text => setEmail({ value: text, error: '' })}
        error={!!email.error}
        errorText={email.error}
        autoCapitalize="none"
        autoComplete="email"
        textContentType="emailAddress"
        keyboardType="email-address"
        description="You will receive an email with password reset instructions."
      />

      <Button mode="contained" onPress={sendResetPasswordEmail} style={{ marginTop: 16 }}>
        <Text style={appStyles.buttonText}>Send Instructions</Text>
      </Button>

      <Breaker color="grey" height={2} />

      <Button mode="contained" onPress={backToLogin} style={{ marginTop: 16 }}>
        <Text style={appStyles.buttonText}>Back to Login</Text>
      </Button>
    </Background>
  );
};

export default ResetPasswordScreen;
