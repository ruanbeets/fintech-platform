import { useState } from "react";

export default function TransactionForm({
  accounts = [],
  onCreate
}) {

  const [accountId, setAccountId] = useState("");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");

  const handleSubmit = e => {

    e.preventDefault();

    if (!accountId || !amount) return;

    onCreate({
      account_id: accountId,
      amount: Number(amount),
      date,
      category,
      description
    });

    setAmount("");
    setDate("");
    setCategory("");
    setDescription("");

  };

  return (

    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">

      <h2 className="text-xl font-semibold mb-4">
        Add Transaction
      </h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4"
      >

        <select
          value={accountId}
          onChange={e => setAccountId(e.target.value)}
          className="w-full bg-gray-800 p-2 rounded"
        >

          <option value="">
            Select Account
          </option>

          {accounts.map(acc => (

            <option
              key={acc.account_id}
              value={acc.account_id}
            >
              {acc.account_type}
            </option>

          ))}

        </select>

        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={e => setAmount(e.target.value)}
          className="w-full bg-gray-800 p-2 rounded"
        />

        <input
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
          className="w-full bg-gray-800 p-2 rounded"
        />

        <input
          placeholder="Category"
          value={category}
          onChange={e => setCategory(e.target.value)}
          className="w-full bg-gray-800 p-2 rounded"
        />

        <input
          placeholder="Description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          className="w-full bg-gray-800 p-2 rounded"
        />

        <button className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-500">

          Add Transaction

        </button>

      </form>

    </div>

  );

}