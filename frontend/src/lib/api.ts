import axios from "axios";

export const api = axios.create({
    baseURL: "/hyper-ai/api",
    headers: {
        "Content-Type": "application/json",
    },
});
