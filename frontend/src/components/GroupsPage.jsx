import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { getAuthBody } from '../api';
import { jwtDecode } from "jwt-decode";

const GroupsPage = () => {
    const navigate = useNavigate();
    const [groups, setGroups] = useState([]);
    const [selectedGroup, setSelectedGroup] = useState(null);
    const [members, setMembers] = useState([]);
    const [myId, setMyId] = useState('');
    const [myRole, setMyRole] = useState('');
    
    const [createForm, setCreateForm] = useState({ name: '', description: '' });
    const [newMemberId, setNewMemberId] = useState('');
    
    const [editMode, setEditMode] = useState(false);
    const [editForm, setEditForm] = useState({ name: '', description: '' });

    useEffect(() => {
        const token = localStorage.getItem('token');
        if(token) {
            try {
                const decoded = jwtDecode(token);
                setMyId(decoded.id);
            } catch(e){}
        }
        fetchGroups();
    }, []);

    const fetchGroups = async () => {
        try {
            const res = await api.post('/groups/get_user_groups', getAuthBody());
            setGroups(res.data.groups || []);
        } catch (e) {
            console.error(e);
        }
    };

    const handleCreateGroup = async (e) => {
        e.preventDefault();
        try {
            await api.post('/groups/create', getAuthBody(createForm));
            alert("Grupa utworzona!");
            setCreateForm({ name: '', description: '' });
            fetchGroups();
        } catch (e) {
            alert("Błąd: " + (e.response?.data?.detail || e.message));
        }
    };

    const handleSelectGroup = async (group) => {
        setSelectedGroup(group);
        setEditMode(false);
        setMyRole(group.role);
        try {
            const resMembers = await api.post(`/groups/${group.id}/members`, getAuthBody());
            setMembers(resMembers.data.members || []);
        } catch (e) {
            console.error(e);
        }
    };

    const handleAddMember = async (e) => {
        e.preventDefault();
        if (!selectedGroup) return;
        try {
            await api.post(`/groups/${selectedGroup.id}/members/add`, getAuthBody({ user_id: newMemberId }));
            alert("Dodano użytkownika!");
            setNewMemberId('');
            handleSelectGroup(selectedGroup);
        } catch (e) {
            alert("Błąd: " + (e.response?.data?.detail || "Sprawdź UUID"));
        }
    };

    const handleRemoveMember = async (userId) => {
        if (!confirm("Usunąć użytkownika?")) return;
        try {
            await api.post(`/groups/${selectedGroup.id}/members/remove`, getAuthBody({ user_id: userId }));
            handleSelectGroup(selectedGroup);
        } catch (e) { alert("Błąd usuwania"); }
    };

    const handleChangeRole = async (userId, newRole) => {
        try {
            await api.post(`/groups/${selectedGroup.id}/roles/assign`, getAuthBody({ user_id: userId, role: newRole }));
            handleSelectGroup(selectedGroup);
        } catch (e) { alert("Błąd zmiany roli: " + e.response?.data?.detail); }
    };

    const handleUpdateGroup = async (e) => {
        e.preventDefault();
        try {
            await api.put(`/groups/${selectedGroup.id}`, getAuthBody(editForm));
            alert("Grupa zaktualizowana");
            setEditMode(false);
            fetchGroups();
            handleSelectGroup({...selectedGroup, ...editForm});
        } catch (e) { alert("Błąd aktualizacji"); }
    };

    const handleDeleteGroup = async () => {
        if (!confirm("Usunąć grupę trwale?")) return;
        try {
            await api.delete(`/groups/${selectedGroup.id}`, { data: getAuthBody() });
            alert("Grupa usunięta");
            setSelectedGroup(null);
            fetchGroups();
        } catch (e) { alert("Błąd usuwania"); }
    };

    const startEdit = () => {
        setEditForm({ name: selectedGroup.name, description: selectedGroup.description });
        setEditMode(true);
    };

    return (
        <div className="flex h-screen bg-gray-100">
            <div className="w-1/3 bg-white border-r flex flex-col">
                <div className="p-4 bg-slate-800 text-white flex justify-between items-center">
                    <h1 className="font-bold text-xl">👥 Grupy</h1>
                    <button onClick={() => navigate('/')} className="text-xs bg-slate-600 px-2 py-1 rounded hover:bg-slate-500">Mapa 🗺️</button>
                </div>
                
                <div className="p-4 border-b bg-gray-50">
                    <h3 className="text-sm font-bold mb-2 text-gray-600">Utwórz nową grupę</h3>
                    <form onSubmit={handleCreateGroup} className="flex flex-col gap-2">
                        <input className="border p-2 rounded text-sm" placeholder="Nazwa" value={createForm.name} onChange={e => setCreateForm({...createForm, name: e.target.value})} required />
                        <input className="border p-2 rounded text-sm" placeholder="Opis" value={createForm.description} onChange={e => setCreateForm({...createForm, description: e.target.value})} />
                        <button className="bg-green-600 text-white py-1 rounded text-sm hover:bg-green-700 font-bold">+ Stwórz</button>
                    </form>
                </div>

                <div className="flex-1 overflow-y-auto p-2">
                    {groups.map(g => (
                        <div key={g.id} onClick={() => handleSelectGroup(g)} className={`p-3 border-b cursor-pointer hover:bg-blue-50 transition ${selectedGroup?.id === g.id ? 'bg-blue-100 border-l-4 border-blue-500' : ''}`}>
                            <div className="font-bold text-slate-800">{g.name}</div>
                            <div className="text-xs text-gray-500">{g.description}</div>
                            <span className="text-xs bg-gray-200 px-1 rounded text-gray-600 mt-1 inline-block">Rola: {g.role}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="w-2/3 p-8 overflow-y-auto">
                {selectedGroup ? (
                    <div className="bg-white p-6 rounded shadow-lg">
                        {!editMode ? (
                            <div className="flex justify-between items-start mb-6 border-b pb-4">
                                <div>
                                    <h2 className="text-3xl font-bold text-slate-800">{selectedGroup.name}</h2>
                                    <p className="text-gray-600">{selectedGroup.description}</p>
                                    <p className="text-xs text-gray-400 mt-1">ID: {selectedGroup.id}</p>
                                </div>
                                <div className="flex gap-2">
                                    {(myRole === 'owner' || myRole === 'admin') && (
                                        <button onClick={startEdit} className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm font-bold hover:bg-blue-200">Edytuj</button>
                                    )}
                                    {myRole === 'owner' && (
                                        <button onClick={handleDeleteGroup} className="bg-red-100 text-red-700 px-3 py-1 rounded text-sm font-bold hover:bg-red-200">Usuń Grupę</button>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <form onSubmit={handleUpdateGroup} className="mb-6 border-b pb-4 bg-gray-50 p-4 rounded">
                                <h3 className="font-bold text-lg mb-2">Edytuj Grupę</h3>
                                <div className="mb-2">
                                    <label className="text-xs font-bold text-gray-500">Nazwa</label>
                                    <input className="border p-2 rounded w-full" value={editForm.name} onChange={e => setEditForm({...editForm, name: e.target.value})} required />
                                </div>
                                <div className="mb-2">
                                    <label className="text-xs font-bold text-gray-500">Opis</label>
                                    <input className="border p-2 rounded w-full" value={editForm.description} onChange={e => setEditForm({...editForm, description: e.target.value})} />
                                </div>
                                <div className="flex gap-2">
                                    <button className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700">Zapisz</button>
                                    <button type="button" onClick={() => setEditMode(false)} className="bg-gray-300 text-gray-700 px-4 py-1 rounded hover:bg-gray-400">Anuluj</button>
                                </div>
                            </form>
                        )}

                        <div className="mb-6">
                            <h3 className="font-bold text-lg mb-3">Członkowie ({members.length})</h3>
                            <div className="space-y-2">
                                {members.map(m => (
                                    <div key={m.user_id} className="flex justify-between items-center bg-gray-50 p-2 rounded border">
                                        <div className="flex items-center gap-3">
                                            {m.picture_url ? <img src={m.picture_url} className="w-8 h-8 rounded-full object-cover"/> : <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center font-bold text-slate-600">{m.first_name?.[0]}</div>}
                                            <div>
                                                <div className="font-bold text-sm">{m.first_name} {m.last_name}</div>
                                                <div className="text-xs text-gray-500">{m.email}</div>
                                                <div className="text-[10px] text-gray-400 font-mono select-all">{m.user_id}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className={`text-xs font-bold px-2 py-1 rounded ${m.role === 'owner' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'}`}>{m.role.toUpperCase()}</span>
                                            
                                            {myRole === 'owner' && m.user_id !== myId && (
                                                <div className="flex gap-1">
                                                    {m.role === 'member' && <button onClick={() => handleChangeRole(m.user_id, 'admin')} className="text-xs bg-green-200 text-green-800 px-1 rounded hover:bg-green-300">Admin</button>}
                                                    {m.role === 'admin' && <button onClick={() => handleChangeRole(m.user_id, 'member')} className="text-xs bg-gray-200 text-gray-800 px-1 rounded hover:bg-gray-300">Member</button>}
                                                    <button onClick={() => handleRemoveMember(m.user_id)} className="text-xs bg-red-200 text-red-800 px-1 rounded hover:bg-red-300">Usuń</button>
                                                </div>
                                            )}
                                            {myRole === 'admin' && m.role === 'member' && (
                                                <button onClick={() => handleRemoveMember(m.user_id)} className="text-xs bg-red-200 text-red-800 px-1 rounded hover:bg-red-300">Usuń</button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {(myRole === 'owner' || myRole === 'admin') && (
                            <div className="bg-slate-50 p-4 rounded border border-slate-200">
                                <h3 className="font-bold text-sm mb-2 text-slate-700">Dodaj członka</h3>
                                <form onSubmit={handleAddMember} className="flex gap-2">
                                    <input className="border p-2 rounded flex-1 text-sm font-mono" placeholder="Wklej UUID użytkownika..." value={newMemberId} onChange={e => setNewMemberId(e.target.value)} required />
                                    <button className="bg-blue-600 text-white px-4 rounded hover:bg-blue-700 font-bold text-sm">Dodaj</button>
                                </form>
                            </div>
                        )}
                    </div>
                ) : <div className="text-center text-gray-400 mt-20">Wybierz grupę z listy lub stwórz nową.</div>}
            </div>
        </div>
    );
};
export default GroupsPage;