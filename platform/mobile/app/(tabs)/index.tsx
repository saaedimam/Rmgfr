import { Link } from 'expo-router';
import { View, Text, StyleSheet } from 'react-native';

export default function Home() {
  return (
    <View style={s.c}>
      <Text style={s.h1}>Sigma Iori Mobile</Text>
      <Text>Deep links: sigmaiori://app/events</Text>
      <Link href="/(tabs)/events" style={s.link}>Go to Events</Link>
    </View>
  );
}
const s = StyleSheet.create({
  c:{ flex:1, alignItems:'center', justifyContent:'center', padding:24 },
  h1:{ fontSize:22, fontWeight:'bold', marginBottom:12 },
  link:{ color:'#2563eb', marginTop:8 }
});
