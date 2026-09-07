import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../core/apiClient";

const fetchTransactions = async () => {
  const res = await apiClient.get("/transactions");
  return res.data;
};

export const useTransactions = () => {
  return useQuery({
    queryKey: ["transactions"],
    queryFn: fetchTransactions,
  });
};