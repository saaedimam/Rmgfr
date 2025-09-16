/**
 * Push notification utilities for Anti-Fraud Mobile app
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export interface PushToken {
  token: string;
  type: 'expo' | 'fcm' | 'apns';
}

export class PushNotificationService {
  private static instance: PushNotificationService;
  private pushToken: string | null = null;

  static getInstance(): PushNotificationService {
    if (!PushNotificationService.instance) {
      PushNotificationService.instance = new PushNotificationService();
    }
    return PushNotificationService.instance;
  }

  async registerForPushNotifications(): Promise<string | null> {
    if (!Device.isDevice) {
      console.log('Must use physical device for Push Notifications');
      return null;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Failed to get push token for push notification!');
      return null;
    }

    try {
      const token = (await Notifications.getExpoPushTokenAsync()).data;
      this.pushToken = token;
      console.log('Push token:', token);
      return token;
    } catch (error) {
      console.error('Error getting push token:', error);
      return null;
    }
  }

  async sendTokenToServer(projectId: string, userId: string): Promise<boolean> {
    if (!this.pushToken) {
      console.log('No push token available');
      return false;
    }

    try {
      const response = await fetch(`${process.env.EXPO_PUBLIC_API_URL}/v1/push-tokens`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          user_id: userId,
          token: this.pushToken,
          platform: Platform.OS,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to register push token: ${response.status}`);
      }

      console.log('Push token registered successfully');
      return true;
    } catch (error) {
      console.error('Error registering push token:', error);
      return false;
    }
  }

  async scheduleLocalNotification(
    title: string,
    body: string,
    data?: Record<string, any>
  ): Promise<string> {
    return await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
        sound: 'default',
      },
      trigger: null, // Send immediately
    });
  }

  async cancelNotification(notificationId: string): Promise<void> {
    await Notifications.cancelScheduledNotificationAsync(notificationId);
  }

  async cancelAllNotifications(): Promise<void> {
    await Notifications.cancelAllScheduledNotificationsAsync();
  }

  addNotificationListener(
    listener: (notification: Notifications.Notification) => void
  ): Notifications.Subscription {
    return Notifications.addNotificationReceivedListener(listener);
  }

  addNotificationResponseListener(
    listener: (response: Notifications.NotificationResponse) => void
  ): Notifications.Subscription {
    return Notifications.addNotificationResponseReceivedListener(listener);
  }

  getPushToken(): string | null {
    return this.pushToken;
  }
}

export const pushNotificationService = PushNotificationService.getInstance();