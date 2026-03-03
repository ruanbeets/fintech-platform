export default function Sidebar() {
  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 p-6">
      <h2 className="text-xl font-bold mb-8">Fintech</h2>

      <nav className="space-y-4 text-gray-400">
        <div className="hover:text-white cursor-pointer">Dashboard</div>
        <div className="hover:text-white cursor-pointer">Accounts</div>
        <div className="hover:text-white cursor-pointer">Analytics</div>
        <div className="hover:text-white cursor-pointer">Settings</div>
      </nav>
    </div>
  );
}