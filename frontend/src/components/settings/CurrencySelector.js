import { useState, useEffect } from "react";

export default function CurrencySelector() {

  const [currency, setCurrency] = useState("USD");

  useEffect(() => {

    const saved = localStorage.getItem("currency");

    if (saved) setCurrency(saved);

  }, []);

  const handleChange = e => {

    const value = e.target.value;

    setCurrency(value);

    localStorage.setItem("currency", value);

  };

  return (

    <div>

      <label className="block text-sm text-gray-400 mb-2">
        Currency
      </label>

      <select
        value={currency}
        onChange={handleChange}
        className="bg-gray-800 border border-gray-700 p-2 rounded w-48"
      >

        <option value="USD">USD</option>
        <option value="ZAR">ZAR</option>
        <option value="EUR">EUR</option>
        <option value="GBP">GBP</option>

      </select>

    </div>

  );

}