import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const Register = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({ email: '', password: '', first_name: '', last_name: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/users/create', formData);
            alert("Konto utworzone! Możesz się zalogować.");
            navigate('/login');
        } catch (err) {
            console.error(err);
            alert('Błąd rejestracji. Sprawdź konsolę.');
        }
    };

    return (
        <div className="flex justify-center items-center h-full bg-slate-100">
            <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow-md w-96 flex flex-col gap-3">
                <h2 className="text-2xl font-bold mb-4">Rejestracja</h2>
                <input placeholder="Imię" required className="border p-2 rounded" onChange={e => setFormData({...formData, first_name: e.target.value})} />
                <input placeholder="Nazwisko" required className="border p-2 rounded" onChange={e => setFormData({...formData, last_name: e.target.value})} />
                <input type="email" placeholder="Email" required className="border p-2 rounded" onChange={e => setFormData({...formData, email: e.target.value})} />
                <input type="password" placeholder="Hasło" required className="border p-2 rounded" onChange={e => setFormData({...formData, password: e.target.value})} />
                <button className="bg-blue-600 text-white p-2 rounded mt-2">Zarejestruj</button>
            </form>
        </div>
    );
};
export default Register;