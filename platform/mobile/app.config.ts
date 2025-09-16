import { ExpoConfig } from 'expo/config';

const scheme = 'sigmaiori';               // your deep link scheme
const host = 'app';                        // optional host for universal links
const bundleId = 'com.yourco.sigmaiori';   // change to your id
const pkg = 'com.yourco.sigmaiori';

const config: ExpoConfig = {
  name: 'Sigma Iori',
  slug: 'sigma-iori',
  scheme,
  ios: { bundleIdentifier: bundleId, supportsTablet: false },
  android: { package: pkg, adaptiveIcon: { foregroundImage: './assets/adaptive-icon.png', backgroundColor: '#ffffff' } },
  web: { bundler: 'metro' },
  extra: {
    // NEXT_PUBLIC_BASE of your web deploy, fallback to localhost for dev
    mobileProxyBase: process.env.MOBILE_PROXY_BASE ?? 'http://localhost:3000',
  },
  experiments: { typedRoutes: true },
};

export default config;
