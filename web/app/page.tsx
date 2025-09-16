import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Anti-Fraud Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Comprehensive fraud detection and prevention platform that protects 
            businesses from financial losses through real-time transaction monitoring.
          </p>
          
          <div className="flex gap-4 justify-center mb-12">
            <Link href="/dashboard">
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                Go to Dashboard
              </button>
            </Link>
            <Link href="/api/health">
              <button className="bg-white hover:bg-gray-50 text-blue-600 px-6 py-3 rounded-lg font-medium border border-blue-600 transition-colors">
                Check API Health
              </button>
            </Link>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-2">Real-time Detection</h3>
              <p className="text-gray-600">
                Monitor transactions in real-time with advanced fraud detection algorithms.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-2">Risk Assessment</h3>
              <p className="text-gray-600">
                Get instant risk scores and automated decision making for every transaction.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-2">Case Management</h3>
              <p className="text-gray-600">
                Manage fraud cases with comprehensive investigation and resolution tools.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
