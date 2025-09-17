'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  Shield, 
  Activity, 
  TestTube, 
  BarChart3, 
  Settings,
  Home
} from 'lucide-react';

const navigation = [
  { name: 'Overview', href: '/dashboard/fraud', icon: Home },
  { name: 'Real-time', href: '/dashboard/fraud/realtime', icon: Activity },
  { name: 'Test Events', href: '/dashboard/fraud/test', icon: TestTube },
  { name: 'Analytics', href: '/dashboard/fraud/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/dashboard/fraud/settings', icon: Settings },
];

export default function FraudNav() {
  const pathname = usePathname();

  return (
    <nav className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
      {navigation.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
              isActive
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            )}
          >
            <item.icon className="h-4 w-4 mr-2" />
            {item.name}
          </Link>
        );
      })}
    </nav>
  );
}
