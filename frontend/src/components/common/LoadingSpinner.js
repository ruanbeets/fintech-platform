export default function LoadingSpinner({
  text = "Loading..."
}) {

  return (

    <div className="flex flex-col items-center justify-center py-16">

      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>

      <p className="text-gray-400 mt-4 text-sm">
        {text}
      </p>

    </div>

  );
}