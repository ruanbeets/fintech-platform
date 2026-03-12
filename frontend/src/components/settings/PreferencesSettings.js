export default function PreferencesSettings() {

  const toggleAnalytics = () => {

    const current =
      localStorage.getItem("analytics");

    const next =
      current === "true" ? "false" : "true";

    localStorage.setItem("analytics", next);

  };

  return (

    <div className="space-y-3">

      <div className="flex justify-between">

        <span className="text-gray-400">
          Enable analytics tracking
        </span>

        <button
          onClick={toggleAnalytics}
          className="bg-gray-800 px-3 py-1 rounded"
        >
          Toggle
        </button>

      </div>

    </div>

  );

}