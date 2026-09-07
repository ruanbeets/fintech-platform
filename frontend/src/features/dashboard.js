import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../core/apiClient";
import { importClient, sessionToken } from "./imports";

export const useDashboard = ({ demo = false, imported = false, userId, month, currency } = {}) =>
  useQuery({
    queryKey: ["dashboard", imported ? sessionToken() : demo ? "local-demo" : userId, month, currency],
    queryFn: async () => {
      const { data } = await (imported || demo ? importClient : apiClient).get(imported ? "/imports/analytics" : demo ? "/dashboard/demo" : `/dashboard/${userId}`, {
        params: { month: month || undefined, currency: currency || undefined },
      });
      return data;
    },
    enabled: imported || demo || Boolean(userId),
    retry: false,
  });
