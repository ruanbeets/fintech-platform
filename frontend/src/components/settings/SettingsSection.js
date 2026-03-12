export default function SettingsSection({
  title,
  children
}) {

  return (

    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">

      <h2 className="text-xl font-semibold mb-4">
        {title}
      </h2>

      {children}

    </div>

  );

}