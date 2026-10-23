import axios from "axios";

const configuredUrl = import.meta.env.VITE_API_URL?.trim();

export const API_URL = (
  configuredUrl || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export const WS_URL = API_URL.replace(/^http/, "ws");

export const api = axios.create({
  baseURL: API_URL,
});