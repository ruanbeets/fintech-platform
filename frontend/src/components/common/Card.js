export default function Card({
  title,
  children
}) {

  return (

    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">

      {title && (
        <h2 className="text-xl font-semibold mb-4">
          {title}
        </h2>
      )}

      {children}

    </div>

  );
}