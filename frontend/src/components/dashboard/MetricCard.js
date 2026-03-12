export default function MetricCard({
  title,
  value,
  subtitle,
  color = "text-white"
}) {

  return (

    <div className="bg-gray-900 border border-gray-800 p-5 rounded-xl">

      <p className="text-gray-400 text-sm">
        {title}
      </p>

      <p className={`text-2xl font-semibold mt-1 ${color}`}>
        {value}
      </p>

      {subtitle && (
        <p className="text-xs text-gray-500 mt-2">
          {subtitle}
        </p>
      )}

    </div>

  );
}