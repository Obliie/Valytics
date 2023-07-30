import React from 'react';
import { StyleSheet, View } from 'react-native';

const Breaker = ({ color = '#ccc', height = 1 }) => {
  return <View style={[styles.breaker, { backgroundColor: color, height }]} />;
};

const styles = StyleSheet.create({
  breaker: {
    width: '100%',
    marginTop: '5%',
    marginBottom: ' 5%',
  },
});

export default Breaker;
