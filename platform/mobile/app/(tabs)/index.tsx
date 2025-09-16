import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function DashboardScreen() {
  const stats = [
    { title: 'Total Events', value: '12,543', change: '+12%', color: '#3b82f6' },
    { title: 'Fraud Detected', value: '234', change: '-8%', color: '#ef4444' },
    { title: 'Approved', value: '11,892', change: '+15%', color: '#10b981' },
    { title: 'Review Cases', value: '417', change: '+3%', color: '#f59e0b' },
  ];

  const recentEvents = [
    { id: '1', type: 'checkout', status: 'processed', time: '10:30 AM' },
    { id: '2', type: 'login', status: 'flagged', time: '10:25 AM' },
    { id: '3', type: 'signup', status: 'processed', time: '10:20 AM' },
    { id: '4', type: 'checkout', status: 'review', time: '10:15 AM' },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Dashboard</Text>
        <Text style={styles.subtitle}>Fraud Detection Overview</Text>
      </View>

      <View style={styles.statsContainer}>
        {stats.map((stat, index) => (
          <View key={index} style={[styles.statCard, { borderLeftColor: stat.color }]}>
            <Text style={styles.statValue}>{stat.value}</Text>
            <Text style={styles.statTitle}>{stat.title}</Text>
            <Text style={[styles.statChange, { color: stat.color }]}>
              {stat.change}
            </Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Events</Text>
        {recentEvents.map((event) => (
          <TouchableOpacity key={event.id} style={styles.eventCard}>
            <View style={styles.eventInfo}>
              <View style={[styles.eventDot, { 
                backgroundColor: event.status === 'processed' ? '#10b981' : 
                               event.status === 'flagged' ? '#ef4444' : '#f59e0b'
              }]} />
              <View>
                <Text style={styles.eventType}>{event.type}</Text>
                <Text style={styles.eventStatus}>{event.status}</Text>
              </View>
            </View>
            <Text style={styles.eventTime}>{event.time}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    padding: 20,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 4,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  statTitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  statChange: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 4,
  },
  section: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  eventCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  eventInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  eventDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 12,
  },
  eventType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  eventStatus: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  eventTime: {
    fontSize: 14,
    color: '#6b7280',
  },
});
