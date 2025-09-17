import { ExpoConfig } from 'expo/config';
const channel = process.env.RELEASE_CHANNEL || 'dev';  // dev|beta|prod

const config: ExpoConfig = {
  name: 'Anti-Fraud Platform',
  slug: 'antifraud-platform',
  scheme: 'antifraud',
  ios: { bundleIdentifier: 'com.antifraud.platform' },
  android: { package: 'com.antifraud.platform' },
  plugins: [
    'expo-font'
  ],
  extra: {
    mobileProxyBase: process.env.MOBILE_PROXY_BASE ?? 'http://localhost:3000',
    releaseChannel: channel,
  },
  updates: { url: 'https://u.expo.dev/<your-project-id>' }, // optional if using EAS Update
  runtimeVersion: { policy: 'sdkVersion' }
};
export default config;
