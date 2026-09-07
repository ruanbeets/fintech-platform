import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../core/apiClient";

const fetchAccounts = async () => {
  const res = await apiClient.get("/accounts");
  return res.data;
};

export const useAccounts = () => {
  return useQuery({
    queryKey: ["accounts"],
    queryFn: fetchAccounts,
  });
};