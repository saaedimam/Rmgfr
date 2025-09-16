import { auth } from "@clerk/nextjs";
import { redirect } from "next/navigation";
import { Nav } from "@/components/Nav";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { userId } = await auth();
  
  if (!userId) {
    redirect("/");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}
