import { useState } from 'react';
import api from '../api';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/users/login', { email, password });
            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                window.location.href = '/'; 
            }
        } catch (err) {
            alert('Błąd logowania.');
        }
    };

    return (
        <div className="flex justify-center items-center h-full bg-slate-100">
            <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-96 flex flex-col gap-3">
                <h2 className="text-2xl font-bold mb-4">Logowanie</h2>
                <input type="email" placeholder="Email" required className="border p-2 rounded" value={email} onChange={e => setEmail(e.target.value)} />
                <input type="password" placeholder="Hasło" required className="border p-2 rounded" value={password} onChange={e => setPassword(e.target.value)} />
                <button className="bg-blue-600 text-white p-2 rounded mt-2">Zaloguj</button>
            </form>
        </div>
    );
};
export default Login;