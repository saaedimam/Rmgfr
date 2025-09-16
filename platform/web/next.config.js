const { withSentryConfig } = require('@sentry/nextjs');

const nextConfig = { reactStrictMode: true };
module.exports = withSentryConfig(nextConfig, { silent: true });