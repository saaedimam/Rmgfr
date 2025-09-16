import * as Sentry from '@sentry/react-native';
import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Constants from 'expo-constants';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  enableAutoPerformanceTracing: true,
  tracesSampleRate: 1.0,
  environment: (Constants?.expoConfig?.extra as any)?.releaseChannel || 'dev',
});

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <Stack screenOptions={{ headerShown: true }} />
    </SafeAreaProvider>
  );
}
