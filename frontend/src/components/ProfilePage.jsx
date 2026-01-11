import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { getAuthBody } from '../api';
import { jwtDecode } from "jwt-decode";

const ProfilePage = () => {
    const navigate = useNavigate();
    
    const [profile, setProfile] = useState({
        id: '',
        email: '',
        first_name: '',
        last_name: '',
        profile_picture: '',
        description: ''
    });

    const [passwords, setPasswords] = useState({
        old_password: '',
        new_password: ''
    });

    const [deletePassword, setDeletePassword] = useState('');
    const [msg, setMsg] = useState({ text: '', type: '' });

    useEffect(() => {
        fetchUserProfile();
    }, []);

    const fetchUserProfile = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/');
            return;
        }
        try {
            const decoded = jwtDecode(token);
            // 1. Ustawiamy podstawowe dane z tokena (żeby coś było widać od razu)
            setProfile(prev => ({
                ...prev,
                id: decoded.id,
                email: decoded.sub,
                first_name: decoded.first_name,
                last_name: decoded.last_name,
                profile_picture: decoded.profile_picture_url
            }));

            // 2. Pobieramy PEŁNE dane z bazy (w tym opis), używając ID z tokena
            // Endpoint to GET /api/v1/users/{userid}
            if (decoded.id) {
                const res = await api.get(`/users/${decoded.id}`);
                const data = res.data;
                
                setProfile({
                    id: data.id,
                    email: data.email,
                    first_name: data.first_name,
                    last_name: data.last_name,
                    profile_picture: data.profile_picture,
                    description: data.description || '' // Tu wpadnie opis z bazy
                });
            }
        } catch (e) {
            console.error("Błąd pobierania profilu:", e);
        }
    };

    const handleUpdateData = async (e) => {
        e.preventDefault();
        setMsg({ text: '', type: '' });
        try {
            const body = getAuthBody({
                email: profile.email,
                first_name: profile.first_name,
                last_name: profile.last_name,
                profile_picture: profile.profile_picture,
                description: profile.description
            });

            const res = await api.post('/users/update/data', body);

            if (res.data.access_token) {
                localStorage.setItem('token', res.data.access_token);
                setMsg({ text: '✅ Dane zaktualizowane pomyślnie!', type: 'success' });
                // Po zapisie nie musimy nic robić, stan profile jest już zaktualizowany przez inputy
            }
        } catch (e) {
            setMsg({ text: '❌ Błąd aktualizacji: ' + (e.response?.data?.detail || e.message), type: 'error' });
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        setMsg({ text: '', type: '' });
        try {
            const body = getAuthBody({
                email: profile.email,
                old_password: passwords.old_password,
                new_password: passwords.new_password
            });

            await api.post('/users/update/password', body);
            setMsg({ text: '✅ Hasło zmienione!', type: 'success' });
            setPasswords({ old_password: '', new_password: '' });
        } catch (e) {
            setMsg({ text: '❌ Błąd zmiany hasła: ' + (e.response?.data?.detail || "Sprawdź stare hasło"), type: 'error' });
        }
    };

    const handleDeleteAccount = async () => {
        if (!deletePassword) {
            alert("Podaj hasło aby usunąć konto.");
            return;
        }
        if (!confirm("Czy na pewno? Tej operacji nie da się cofnąć.")) return;

        try {
            const body = getAuthBody({
                password: deletePassword
            });

            // Używamy ID z profilu lub emaila, zależnie jak backend woli, ale endpoint delete_user_api bierze {userid}
            await api.delete(`/users/${profile.email}`, { data: body });
            
            alert("Konto usunięte.");
            localStorage.removeItem('token');
            navigate('/login');
        } catch (e) {
            alert('❌ Błąd usuwania: ' + (e.response?.data?.detail || e.message));
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4 flex justify-center items-start">
            <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-3xl mt-10">
                <div className="flex justify-between items-center mb-6 border-b pb-4">
                    <h1 className="text-3xl font-bold text-slate-800">👤 Edycja Profilu</h1>
                    <button onClick={() => navigate('/')} className="text-blue-600 hover:bg-blue-50 px-3 py-1 rounded font-bold transition">
                        ← Powrót do Mapy
                    </button>
                </div>

                {msg.text && (
                    <div className={`p-4 mb-6 rounded text-center font-bold ${msg.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {msg.text}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    
                    <form onSubmit={handleUpdateData} className="flex flex-col gap-4">
                        <h2 className="text-xl font-bold text-gray-700 border-b pb-2">Dane Osobowe</h2>
                        
                        <div>
                            <label className="text-xs font-bold text-gray-500">TWOJE UUID (Do zaproszeń)</label>
                            <input 
                                className="border p-2 rounded w-full bg-gray-100 text-gray-600 font-mono text-xs select-all" 
                                value={profile.id} 
                                readOnly 
                            />
                        </div>

                        <div className="flex gap-2">
                            <div className="w-1/2">
                                <label className="text-xs font-bold text-gray-500">IMIĘ</label>
                                <input className="border p-2 rounded w-full" value={profile.first_name} onChange={e=>setProfile({...profile, first_name: e.target.value})} />
                            </div>
                            <div className="w-1/2">
                                <label className="text-xs font-bold text-gray-500">NAZWISKO</label>
                                <input className="border p-2 rounded w-full" value={profile.last_name} onChange={e=>setProfile({...profile, last_name: e.target.value})} />
                            </div>
                        </div>

                        <div>
                            <label className="text-xs font-bold text-gray-500">URL ZDJĘCIA</label>
                            <input className="border p-2 rounded w-full" value={profile.profile_picture} onChange={e=>setProfile({...profile, profile_picture: e.target.value})} />
                            {profile.profile_picture && <img src={profile.profile_picture} alt="Preview" className="w-16 h-16 rounded-full mt-2 object-cover border" />}
                        </div>

                        <div>
                            <label className="text-xs font-bold text-gray-500">OPIS</label>
                            <textarea 
                                className="border p-2 rounded w-full h-20" 
                                value={profile.description} 
                                onChange={e=>setProfile({...profile, description: e.target.value})} 
                                placeholder="Napisz coś o sobie..."
                            />
                        </div>

                        <button className="bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition font-bold shadow">
                            Zapisz Zmiany
                        </button>
                    </form>

                    <div className="flex flex-col gap-8">
                        
                        <form onSubmit={handleChangePassword} className="flex flex-col gap-4 bg-gray-50 p-4 rounded border">
                            <h2 className="text-lg font-bold text-gray-700">Zmiana Hasła</h2>
                            <input 
                                type="password" 
                                className="border p-2 rounded w-full" 
                                placeholder="Stare hasło" 
                                value={passwords.old_password}
                                onChange={e=>setPasswords({...passwords, old_password: e.target.value})} 
                            />
                            <input 
                                type="password" 
                                className="border p-2 rounded w-full" 
                                placeholder="Nowe hasło" 
                                value={passwords.new_password}
                                onChange={e=>setPasswords({...passwords, new_password: e.target.value})} 
                            />
                            <button className="bg-orange-500 text-white py-2 rounded hover:bg-orange-600 transition font-bold">
                                Zmień Hasło
                            </button>
                        </form>

                        <div className="border border-red-200 p-4 rounded bg-red-50">
                            <h2 className="text-lg font-bold text-red-700 mb-2">Strefa Niebezpieczna</h2>
                            <p className="text-xs text-red-600 mb-3">Aby usunąć konto, podaj swoje hasło.</p>
                            <div className="flex gap-2">
                                <input 
                                    type="password" 
                                    className="border border-red-300 p-2 rounded flex-1" 
                                    placeholder="Twoje hasło"
                                    value={deletePassword}
                                    onChange={e=>setDeletePassword(e.target.value)}
                                />
                                <button onClick={handleDeleteAccount} className="bg-red-600 text-white px-4 rounded hover:bg-red-700 font-bold">
                                    USUŃ
                                </button>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;