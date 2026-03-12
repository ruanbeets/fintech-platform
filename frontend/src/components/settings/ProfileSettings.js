export default function ProfileSettings() {

  const email = localStorage.getItem("user_email");

  return (

    <div>

      <p className="text-gray-400 text-sm mb-1">
        Email
      </p>

      <p className="text-lg font-semibold">
        {email}
      </p>

      <p className="text-xs text-gray-500 mt-2">
        Profile management coming soon
      </p>

    </div>

  );

}