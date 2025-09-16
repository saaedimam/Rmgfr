import { ExpoConfig } from 'expo/config';
const channel = process.env.RELEASE_CHANNEL || 'dev';  // dev|beta|prod

const config: ExpoConfig = {
  name: 'Sigma Iori',
  slug: 'sigma-iori',
  scheme: 'sigmaiori',
  ios: { bundleIdentifier: 'com.yourco.sigmaiori' },
  android: { package: 'com.yourco.sigmaiori' },
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
