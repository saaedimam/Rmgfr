import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';

const base = (Constants?.expoConfig?.extra as any)?.mobileProxyBase || 'http://localhost:3000';

Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: false, shouldSetBadge: false }),
});

export async function registerForPushAsync(userId?: string, deviceHash?: string) {
  if (!Device.isDevice) return { ok:false, reason:'simulator' };
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== 'granted') return { ok:false, reason:'no-permission' };
  const token = (await Notifications.getExpoPushTokenAsync()).data;
  // send to server proxy → API (uses server PROJECT_API_KEY)
  const r = await fetch(`${base}/api/mobile/events`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ type:'push_register', payload:{ token } }) });
  // optionally call a special endpoint:
  await fetch(`${base}/api/mobile/register-push`, {  // we'll add this proxy below
    method:'POST', headers:{ 'Content-Type':'application/json' },
    body: JSON.stringify({ expo_push_token: token, user_id: userId, device_hash: deviceHash, platform: Device.osName })
  });
  return { ok:true, token };
}
