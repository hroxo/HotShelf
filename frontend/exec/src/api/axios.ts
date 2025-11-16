import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/state",
  timeout: 15000,
});

export default api;
