import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function EventsScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState('all');

  const events = [
    { id: '1', type: 'checkout', amount: '$299.99', status: 'processed', time: '10:30 AM', risk: 'Low' },
    { id: '2', type: 'login', amount: '-', status: 'flagged', time: '10:25 AM', risk: 'High' },
    { id: '3', type: 'signup', amount: '-', status: 'processed', time: '10:20 AM', risk: 'Low' },
    { id: '4', type: 'checkout', amount: '$1,299.99', status: 'review', time: '10:15 AM', risk: 'Medium' },
    { id: '5', type: 'login', amount: '-', status: 'processed', time: '10:10 AM', risk: 'Low' },
    { id: '6', type: 'checkout', amount: '$49.99', status: 'denied', time: '10:05 AM', risk: 'High' },
  ];

  const filteredEvents = events.filter(event => {
    const matchesSearch = event.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         event.amount.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filter === 'all' || event.status === filter;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed': return '#10b981';
      case 'flagged': return '#f59e0b';
      case 'review': return '#3b82f6';
      case 'denied': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low': return '#10b981';
      case 'Medium': return '#f59e0b';
      case 'High': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const renderEvent = ({ item }: { item: any }) => (
    <TouchableOpacity style={styles.eventCard}>
      <View style={styles.eventHeader}>
        <View style={styles.eventInfo}>
          <Text style={styles.eventType}>{item.type}</Text>
          <Text style={styles.eventAmount}>{item.amount}</Text>
        </View>
        <View style={styles.eventStatus}>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
            <Text style={styles.statusText}>{item.status}</Text>
          </View>
          <Text style={styles.eventTime}>{item.time}</Text>
        </View>
      </View>
      <View style={styles.eventFooter}>
        <View style={styles.riskIndicator}>
          <Ionicons name="shield" size={16} color={getRiskColor(item.risk)} />
          <Text style={[styles.riskText, { color: getRiskColor(item.risk) }]}>
            {item.risk} Risk
          </Text>
        </View>
        <Ionicons name="chevron-forward" size={20} color="#6b7280" />
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Events</Text>
        <Text style={styles.subtitle}>Transaction monitoring</Text>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchInput}>
          <Ionicons name="search" size={20} color="#6b7280" />
          <TextInput
            style={styles.searchText}
            placeholder="Search events..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
      </View>

      <View style={styles.filterContainer}>
        {['all', 'processed', 'flagged', 'review', 'denied'].map((filterType) => (
          <TouchableOpacity
            key={filterType}
            style={[
              styles.filterButton,
              filter === filterType && styles.filterButtonActive
            ]}
            onPress={() => setFilter(filterType)}
          >
            <Text style={[
              styles.filterText,
              filter === filterType && styles.filterTextActive
            ]}>
              {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filteredEvents}
        renderItem={renderEvent}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.eventsList}
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
  searchContainer: {
    padding: 16,
    backgroundColor: '#ffffff',
  },
  searchInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f3f4f6',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  searchText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 16,
    color: '#1f2937',
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 16,
    backgroundColor: '#ffffff',
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
  },
  filterButtonActive: {
    backgroundColor: '#3b82f6',
  },
  filterText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },
  filterTextActive: {
    color: '#ffffff',
  },
  eventsList: {
    padding: 16,
  },
  eventCard: {
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
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  eventInfo: {
    flex: 1,
  },
  eventType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    textTransform: 'capitalize',
  },
  eventAmount: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  eventStatus: {
    alignItems: 'flex-end',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 4,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
    textTransform: 'capitalize',
  },
  eventTime: {
    fontSize: 12,
    color: '#6b7280',
  },
  eventFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  riskIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  riskText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4,
  },
});