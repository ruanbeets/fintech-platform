export default function SettingsPage() {

  const email = localStorage.getItem("user_email");

  return (
    <div>

      <h1 className="text-4xl font-bold mb-8">
        Settings
      </h1>

      <div className="bg-gray-900 p-6 rounded-xl">

        <p className="text-gray-400">
          Logged in as:
        </p>

        <p className="text-lg font-medium">
          {email}
        </p>

      </div>

    </div>
  );
}