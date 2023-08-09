import React from 'react';
import { Text } from 'react-native-paper';

import Background from '../components/Background';
import Button from '../components/Button';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Paragraph from '../components/Paragraph';
import { DashboardNavigationProp, DashboardRouteProp } from '../helpers/NavigationTypes';
import { appStyles } from '../theme/mainStyles';

interface DashboardProps {
  navigation: DashboardNavigationProp;
  route: DashboardRouteProp;
}

const Dashboard: React.FC<DashboardProps> = ({ navigation, route }) => {
  return (
    <Background>
      <Logo />
      <Header>Valytics</Header>
      {/* Display entered email */}
      <Paragraph>Email: {route.params?.email}</Paragraph>
      <Button
        mode="contained"
        onPress={() =>
          navigation.reset({
            index: 0,
            routes: [{ name: 'LoginScreen' }],
          })
        }>
        <Text style={appStyles.buttonText}>Logout</Text>
      </Button>
    </Background>
  );
};

export default Dashboard;
