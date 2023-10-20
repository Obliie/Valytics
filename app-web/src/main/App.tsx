import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { registerRootComponent } from 'expo';
import { Provider } from 'react-native-paper';

import React from 'react';
import { RootStackParamList } from '../helpers/NavigationTypes';
import { Dashboard, LoginScreen, RegisterScreen, ResetPasswordScreen } from '../screens';
import { theme } from '../theme/theme';

const Stack = createStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <Provider theme={theme}>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="LoginScreen"
          screenOptions={{
            headerShown: false,
          }}>
          <Stack.Screen name="LoginScreen" component={LoginScreen} />
          <Stack.Screen name="RegisterScreen" component={RegisterScreen} />
          <Stack.Screen name="Dashboard" component={Dashboard} />
          <Stack.Screen name="ResetPasswordScreen" component={ResetPasswordScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </Provider>
  );
}

registerRootComponent(App);
