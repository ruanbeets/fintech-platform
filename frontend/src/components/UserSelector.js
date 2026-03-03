export default function UserSelector({ users, setSelectedUser }) {
  return (
    <div className="mb-8">
      <label className="block text-sm text-gray-400 mb-2">
        Select User
      </label>
      <select
        onChange={(e) => setSelectedUser(e.target.value)}
        className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-64"
      >
        <option value="">-- Choose User --</option>
        {users.map(user => (
          <option key={user.user_id} value={user.user_id}>
            {user.email}
          </option>
        ))}
      </select>
    </div>
  );
}