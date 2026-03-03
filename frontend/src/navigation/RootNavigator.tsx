import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { ActivityIndicator, View } from 'react-native';

import { useAuthStore } from '../store/authStore';
import { getToken } from '../services/api';
import { Colors } from '../utils/theme';

import LoginScreen from '../screens/LoginScreen';
import AuthCallbackScreen from '../screens/AuthCallbackScreen';
import MainTabNavigator from './MainTabNavigator';
import ChatRoomScreen from '../screens/ChatRoomScreen';
import ExperimentDetailScreen from '../screens/ExperimentDetailScreen';
import ExperimentEditorScreen from '../screens/ExperimentEditorScreen';

const Stack = createStackNavigator();

const linking = {
  prefixes: ['otherus://', 'http://localhost:8080', 'https://otherus.app'],
  config: {
    screens: {
      AuthCallback: 'auth-callback',
      Login: 'login',
      Main: {
        screens: {
          Profile: 'profile',
          Community: 'community',
          Experiments: 'experiments',
          Chat: 'chat',
          Settings: 'settings',
        },
      },
      ChatRoom: 'chat/:roomId',
      ExperimentDetail: 'experiments/:experimentId',
      ExperimentEditor: 'experiments/:experimentId/edit',
    },
  },
};

export default function RootNavigator() {
  const { user, isLoading, fetchMe } = useAuthStore();
  const [initializing, setInitializing] = React.useState(true);

  useEffect(() => {
    const init = async () => {
      const token = await getToken();
      if (token) {
        await fetchMe();
      }
      setInitializing(false);
    };
    init();
  }, []);

  if (initializing) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer linking={linking}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <>
            <Stack.Screen name="Main" component={MainTabNavigator} />
            <Stack.Screen name="ChatRoom" component={ChatRoomScreen} />
            <Stack.Screen name="ExperimentDetail" component={ExperimentDetailScreen} />
            <Stack.Screen name="ExperimentEditor" component={ExperimentEditorScreen} />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="AuthCallback" component={AuthCallbackScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
