// src/app/providers.jsx

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "../core/queryClient";

export const Providers = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};