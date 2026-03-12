import axios from "axios";

/*
=======================================
API CLIENT
=======================================
*/

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json"
  }
});

/*
=======================================
REQUEST INTERCEPTOR
(Attach auth if needed later)
=======================================
*/

API.interceptors.request.use(config => {

  const userId = localStorage.getItem("user_id");

  if (userId) {
    config.headers["X-User-Id"] = userId;
  }

  return config;

});

/*
=======================================
RESPONSE INTERCEPTOR
(Global error handling)
=======================================
*/

API.interceptors.response.use(

  response => response,

  error => {

    console.error("API Error:", error.response?.data || error.message);

    if (error.response?.status === 401) {

      localStorage.removeItem("user_id");
      localStorage.removeItem("user_email");

      window.location.href = "/";

    }

    return Promise.reject(error);

  }

);

/*
=======================================
AUTH
=======================================
*/

export const login = async (email, password) => {

  const res = await API.post(
    "/api/auth/login",
    { email, password }
  );

  return res.data;

};

/*
=======================================
USERS
=======================================
*/

export const getUsers = async () => {

  const res = await API.get("/api/users/");

  return res.data;

};

/*
=======================================
ACCOUNTS
=======================================
*/

export const getAccounts = async (userId) => {

  const res = await API.get(
    `/api/accounts`,
    { params: { user_id: userId } }
  );

  return res.data;

};

export const getAccount = async (accountId) => {

  const res = await API.get(
    `/api/accounts/${accountId}`
  );

  return res.data;

};

/*
=======================================
TRANSACTIONS
=======================================
*/

export const getTransactions = async (userId) => {

  const res = await API.get(
    `/api/transactions`,
    { params: { user_id: userId } }
  );

  return res.data;

};

export const createTransaction = async (data) => {

  const res = await API.post(
    "/api/transactions",
    data
  );

  return res.data;

};

export const deleteTransaction = async (transactionId) => {

  const res = await API.delete(
    `/api/transactions/${transactionId}`
  );

  return res.data;

};

/*
=======================================
ANALYTICS
=======================================
*/

export const getSummary = async (userId) => {

  const res = await API.get(
    `/api/transactions/summary`,
    { params: { user_id: userId } }
  );

  return res.data;

};

export const getCategorySummary = async (userId) => {

  const res = await API.get(
    `/api/transactions/category-summary`,
    { params: { user_id: userId } }
  );

  return res.data;

};

/*
=======================================
INGESTION (CSV Upload)
=======================================
*/

export const uploadTransactions = async (accountId, file) => {

  const formData = new FormData();

  formData.append("file", file);

  const res = await API.post(
    `/api/ingestion/transactions`,
    formData,
    {
      params: { account_id: accountId },
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  );

  return res.data;

};