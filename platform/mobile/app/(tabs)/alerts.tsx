import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function AlertsScreen() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const alerts = [
    {
      id: '1',
      type: 'fraud_detected',
      title: 'High Risk Transaction',
      message: 'Transaction of $1,299.99 flagged for review',
      time: '10:15 AM',
      severity: 'high',
      read: false,
    },
    {
      id: '2',
      type: 'rule_triggered',
      title: 'Velocity Rule Triggered',
      message: 'User exceeded 10 transactions in 1 hour',
      time: '9:45 AM',
      severity: 'medium',
      read: false,
    },
    {
      id: '3',
      type: 'case_assigned',
      title: 'New Case Assigned',
      message: 'Case #1234 assigned to you for review',
      time: '9:30 AM',
      severity: 'low',
      read: true,
    },
    {
      id: '4',
      type: 'system_alert',
      title: 'System Maintenance',
      message: 'Scheduled maintenance in 2 hours',
      time: '8:00 AM',
      severity: 'info',
      read: true,
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#3b82f6';
      case 'info': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return 'alert-circle';
      case 'medium': return 'warning';
      case 'low': return 'information-circle';
      case 'info': return 'information-circle-outline';
      default: return 'information-circle';
    }
  };

  const renderAlert = ({ item }: { item: any }) => (
    <TouchableOpacity style={[styles.alertCard, !item.read && styles.unreadAlert]}>
      <View style={styles.alertHeader}>
        <View style={styles.alertIcon}>
          <Ionicons 
            name={getSeverityIcon(item.severity)} 
            size={24} 
            color={getSeverityColor(item.severity)} 
          />
        </View>
        <View style={styles.alertContent}>
          <Text style={styles.alertTitle}>{item.title}</Text>
          <Text style={styles.alertMessage}>{item.message}</Text>
          <Text style={styles.alertTime}>{item.time}</Text>
        </View>
        {!item.read && <View style={styles.unreadDot} />}
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Alerts</Text>
        <Text style={styles.subtitle}>Fraud detection notifications</Text>
      </View>

      <View style={styles.settingsCard}>
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Ionicons name="notifications" size={24} color="#3b82f6" />
            <View style={styles.settingText}>
              <Text style={styles.settingTitle}>Push Notifications</Text>
              <Text style={styles.settingDescription}>
                Receive alerts for fraud detection
              </Text>
            </View>
          </View>
          <Switch
            value={notificationsEnabled}
            onValueChange={setNotificationsEnabled}
            trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
            thumbColor={notificationsEnabled ? '#ffffff' : '#ffffff'}
          />
        </View>
      </View>

      <View style={styles.alertsHeader}>
        <Text style={styles.alertsTitle}>Recent Alerts</Text>
        <TouchableOpacity>
          <Text style={styles.markAllRead}>Mark all read</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={alerts}
        renderItem={renderAlert}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.alertsList}
        showsVerticalScrollIndicator={false}
      />
    </View>
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
  settingsCard: {
    backgroundColor: '#ffffff',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 12,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
  },
  settingDescription: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  alertsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  alertsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  markAllRead: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '600',
  },
  alertsList: {
    padding: 16,
  },
  alertCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  unreadAlert: {
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  alertIcon: {
    marginRight: 12,
    marginTop: 2,
  },
  alertContent: {
    flex: 1,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  alertMessage: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
    marginBottom: 8,
  },
  alertTime: {
    fontSize: 12,
    color: '#9ca3af',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#3b82f6',
    marginTop: 4,
  },
});
