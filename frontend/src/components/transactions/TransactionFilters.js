export default function TransactionFilters({
  onSearch
}) {

  return (

    <div className="flex gap-4 mb-4">

      <input
        placeholder="Search transactions"
        onChange={e => onSearch(e.target.value)}
        className="bg-gray-800 p-2 rounded"
      />

      <select
        onChange={e => onSearch(e.target.value)}
        className="bg-gray-800 p-2 rounded"
      >

        <option value="">
          All Categories
        </option>

        <option value="Food">
          Food
        </option>

        <option value="Transport">
          Transport
        </option>

        <option value="Shopping">
          Shopping
        </option>

      </select>

    </div>

  );

}