import { useEffect, useState } from "react";
import { getAccounts } from "../services/api";

import AccountsSection from "../components/AccountsSection";

export default function AccountsPage() {

  const [accounts, setAccounts] = useState([]);

  useEffect(() => {

    const fetchAccounts = async () => {

      const userId = localStorage.getItem("user_id");

      if (!userId) return;

      const data = await getAccounts(userId);

      setAccounts(data);

    };

    fetchAccounts();

  }, []);

  return (
    <div>

      <h1 className="text-4xl font-bold mb-8">
        Accounts
      </h1>

      <AccountsSection accounts={accounts} />

    </div>
  );
}