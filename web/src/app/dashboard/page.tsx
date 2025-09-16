import { StatsCards } from "@/components/dashboard/stats-cards";
import { EventsList } from "@/components/dashboard/events-list";
import { DecisionsList } from "@/components/dashboard/decisions-list";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Overview of your fraud detection system
        </p>
      </div>

      <StatsCards />

      <div className="grid lg:grid-cols-2 gap-8">
        <EventsList />
        <DecisionsList />
      </div>
    </div>
  );
}
