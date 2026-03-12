export default function EmptyState({
  title = "Nothing here yet",
  message = "There is no data to display.",
  action = null
}) {

  return (

    <div className="flex flex-col items-center justify-center text-center py-12">

      <div className="text-4xl mb-4">
        📭
      </div>

      <h3 className="text-lg font-semibold mb-2">
        {title}
      </h3>

      <p className="text-gray-400 max-w-md">
        {message}
      </p>

      {action && (
        <div className="mt-6">
          {action}
        </div>
      )}

    </div>

  );
}