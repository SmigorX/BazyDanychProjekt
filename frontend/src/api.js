import axios from 'axios';

// Adres backendu (Docker)
const API_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_URL,
});

// Helper: Twój backend wymaga tokena w BODY (polu "jwt"), a nie w nagłówku
export const getAuthBody = (data = {}) => {
    const token = localStorage.getItem('token');
    return {
        jwt: token,
        ...data
    };
};

export default api;