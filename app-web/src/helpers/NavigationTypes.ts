import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';

export type RootStackParamList = {
  Dashboard: { email: string };
  LoginScreen: undefined;
  RegisterScreen: undefined;
  ResetPasswordScreen: undefined;
  // Add other routes here
};

// Define navigation prop types for each screen
export type DashboardNavigationProp = StackNavigationProp<RootStackParamList, 'Dashboard'>;
export type LoginScreenNavigationProp = StackNavigationProp<RootStackParamList, 'LoginScreen'>;
export type RegisterScreenNavigationProp = StackNavigationProp<RootStackParamList, 'RegisterScreen'>;
export type ResetPasswordScreenNavigationProp = StackNavigationProp<RootStackParamList, 'ResetPasswordScreen'>;

// Define route prop types for each screen
export type DashboardRouteProp = RouteProp<RootStackParamList, 'Dashboard'>;
export type LoginScreenRouteProp = RouteProp<RootStackParamList, 'LoginScreen'>;
export type RegisterScreenRouteProp = RouteProp<RootStackParamList, 'RegisterScreen'>;
export type ResetPasswordScreenRouteProp = RouteProp<RootStackParamList, 'ResetPasswordScreen'>;
