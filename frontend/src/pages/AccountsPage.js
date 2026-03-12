import { useEffect, useState } from "react";

import TopBar from "../components/layout/TopBar";

import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";

import AccountSelector from "../components/accounts/AccountSelector";
import AccountsSection from "../components/accounts/AccountsSection";

import AccountAllocationChart from "../components/charts/AccountAllocationChart";

import { getAccounts } from "../services/api";

export default function AccountsPage() {

  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const fetchAccounts = async () => {

      const userId = localStorage.getItem("user_id");

      const data = await getAccounts(userId);

      setAccounts(data || []);
      setLoading(false);

    };

    fetchAccounts();

  }, []);

  if (loading) return <LoadingSpinner />;

  return (

    <div>

      <TopBar />

      <PageHeader
        title="Accounts"
        subtitle="View and manage your financial accounts"
      />

      <AccountSelector accounts={accounts} />

      <AccountsSection accounts={accounts} />

      <div className="mt-8">

        <AccountAllocationChart
          accounts={accounts}
        />

      </div>

    </div>

  );

}