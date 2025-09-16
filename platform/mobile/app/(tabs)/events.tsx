import { useEffect, useState } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { postMobileEvent, pingHealth } from '../../lib/api';
import { registerForPushAsync } from '../../lib/push';

export default function Events() {
  const [health, setHealth] = useState<any>(null);
  const [lastId, setLastId] = useState<string|undefined>();
  const [pushToken, setPushToken] = useState<string | undefined>();

  useEffect(() => {
    pingHealth().then(setHealth).catch(()=>{});
  }, []);

  const sendEvent = async () => {
    const resp = await postMobileEvent({ type: 'mobile_login', actor_user_id: 'm-user-1', device_hash: 'device-xyz', payload: { ts: Date.now() } });
    setLastId(resp?.event_id);
  };

  const registerPush = async () => {
    const res = await registerForPushAsync('m-user-1','device-xyz');
    if ((res as any).token) setPushToken((res as any).token);
  };

  return (
    <View style={s.c}>
      <Text style={s.h1}>Mobile → Server Proxy</Text>
      <Text style={s.mono}>{JSON.stringify(health)}</Text>
      <Button title="Send Test Event" onPress={sendEvent} />
      <Button title="Register Push" onPress={registerPush} />
      {pushToken && <Text style={s.id}>Push token: {pushToken}</Text>}
      {lastId && <Text style={s.id}>Last event_id: {lastId}</Text>}
    </View>
  );
}
const s = StyleSheet.create({ c:{ flex:1, padding:16, gap:12 }, h1:{ fontSize:18, fontWeight:'600' }, mono:{ fontFamily:'Courier', fontSize:12, color:'#374151' }, id:{ fontSize:12, color:'#059669' }});
