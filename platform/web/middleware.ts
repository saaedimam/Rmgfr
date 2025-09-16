import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  publicRoutes: ['/', '/sign-in(.*)', '/sign-up(.*)'], // everything else requires auth
});

export const config = {
  matcher: ['/((?!_next|.*\\.(?:svg|png|jpg|jpeg|gif|ico|css|js|map)).*)'],
};
