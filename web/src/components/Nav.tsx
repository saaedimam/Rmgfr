"use client";

import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/dashboard" },
  { name: "Events", href: "/dashboard/events" },
  { name: "Decisions", href: "/dashboard/decisions" },
  { name: "Cases", href: "/dashboard/cases" },
  { name: "Rules", href: "/dashboard/rules" },
  { name: "Settings", href: "/dashboard/settings" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link href="/dashboard" className="text-xl font-bold text-gray-900">
              Anti-Fraud
            </Link>
            <div className="hidden md:flex space-x-6">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    pathname === item.href
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  )}
                >
                  {item.name}
                </Link>
              ))}
            </div>
          </div>
          <UserButton afterSignOutUrl="/" />
        </div>
      </div>
    </nav>
  );
}
