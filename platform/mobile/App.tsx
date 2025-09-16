/**
 * Anti-Fraud Platform Mobile App
 * React Native + Expo application
 */

import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import * as SplashScreen from 'expo-splash-screen';
import * as Font from 'expo-font';
import { Ionicons } from '@expo/vector-icons';

// Keep the splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

interface Item {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  created_at: string;
  updated_at: string;
}

export default function App() {
  const [appIsReady, setAppIsReady] = useState(false);
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function prepare() {
      try {
        // Pre-load fonts, make any API calls you need to do here
        await Font.loadAsync({
          ...Ionicons.font,
        });
      } catch (e) {
        console.warn(e);
      } finally {
        // Tell the application to render
        setAppIsReady(true);
      }
    }

    prepare();
  }, []);

  const onLayoutRootView = React.useCallback(async () => {
    if (appIsReady) {
      // This tells the splash screen to hide immediately
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/items');
      if (response.ok) {
        const data = await response.json();
        setItems(data);
      } else {
        Alert.alert('Error', 'Failed to fetch items');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error occurred');
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const createTestItem = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/items', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'Test Item',
          description: 'A test item from mobile app',
          price: 29.99,
          category: 'mobile-test'
        }),
      });
      
      if (response.ok) {
        Alert.alert('Success', 'Item created successfully');
        fetchItems(); // Refresh the list
      } else {
        Alert.alert('Error', 'Failed to create item');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error occurred');
      console.error('Create error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!appIsReady) {
    return null;
  }

  return (
    <View style={styles.container} onLayout={onLayoutRootView}>
      <StatusBar style="auto" />
      
      <View style={styles.header}>
        <Text style={styles.title}>Anti-Fraud Platform</Text>
        <Text style={styles.subtitle}>Mobile App</Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>API Connection Test</Text>
          <Text style={styles.description}>
            Test connection to the FastAPI backend
          </Text>
          
          <View style={styles.buttonContainer}>
            <TouchableOpacity 
              style={[styles.button, styles.primaryButton]} 
              onPress={fetchItems}
              disabled={loading}
            >
              <Ionicons name="refresh" size={20} color="white" />
              <Text style={styles.buttonText}>
                {loading ? 'Loading...' : 'Fetch Items'}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.button, styles.secondaryButton]} 
              onPress={createTestItem}
              disabled={loading}
            >
              <Ionicons name="add" size={20} color="#007AFF" />
              <Text style={[styles.buttonText, styles.secondaryButtonText]}>
                Create Test Item
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {items.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Items ({items.length})</Text>
            {items.map((item) => (
              <View key={item.id} style={styles.itemCard}>
                <Text style={styles.itemName}>{item.name}</Text>
                <Text style={styles.itemDescription}>{item.description}</Text>
                <View style={styles.itemFooter}>
                  <Text style={styles.itemPrice}>${item.price.toFixed(2)}</Text>
                  <Text style={styles.itemCategory}>{item.category}</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Features</Text>
          <View style={styles.featureList}>
            <View style={styles.featureItem}>
              <Ionicons name="shield-checkmark" size={20} color="#4CAF50" />
              <Text style={styles.featureText}>Fraud Detection</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="analytics" size={20} color="#2196F3" />
              <Text style={styles.featureText}>Real-time Analytics</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="lock-closed" size={20} color="#FF9800" />
              <Text style={styles.featureText}>Secure Authentication</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="notifications" size={20} color="#9C27B0" />
              <Text style={styles.featureText}>Alert System</Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#007AFF',
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
    lineHeight: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 10,
  },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 8,
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  secondaryButton: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  secondaryButtonText: {
    color: '#007AFF',
  },
  itemCard: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  itemName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  itemDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  itemFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemPrice: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  itemCategory: {
    fontSize: 12,
    color: '#999',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  featureList: {
    gap: 12,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 8,
  },
  featureText: {
    fontSize: 16,
    color: '#333',
  },
});

