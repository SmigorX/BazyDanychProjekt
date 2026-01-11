import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, ZoomControl } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from "jwt-decode";
import 'leaflet/dist/leaflet.css';
import api, { getAuthBody } from '../api';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon, shadowUrl: iconShadow,
    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34]
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapClickHandler({ onMapClick }) {
    useMapEvents({ click: (e) => onMapClick(e.latlng) });
    return null;
}

const getColoredIcon = (color) => L.divIcon({
    className: 'custom-icon',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 5px black;"></div>`,
    iconSize: [20, 20], iconAnchor: [10, 10], popupAnchor: [0, -10]
});

const MapPage = () => {
    const navigate = useNavigate();
    const [notes, setNotes] = useState([]);
    const [user, setUser] = useState({ name: 'Użytkownik', picture: '' });
    const [groups, setGroups] = useState([]);

    const [formVisible, setFormVisible] = useState(false);
    const [editMode, setEditMode] = useState(false); 
    const [currentNoteId, setCurrentNoteId] = useState(null); 
    
    const [form, setForm] = useState({ title: '', content: '', color: '#3b82f6', group_id: '' });
    const [notePos, setNotePos] = useState(null); 
    const [sidebarOpen, setSidebarOpen] = useState(true);

    useEffect(() => { 
        fetchNotes(); 
        loadUserInfo();
        fetchGroups();
    }, []);

    const loadUserInfo = () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const decoded = jwtDecode(token);
                const name = decoded.first_name ? `${decoded.first_name} ${decoded.last_name}` : (decoded.sub || 'Użytkownik');
                const picture = decoded.profile_picture_url || '';
                setUser({ name, picture });
            } catch (e) { console.error(e); }
        }
    };

    const fetchGroups = async () => {
        try {
            const res = await api.post('/groups/get_user_groups', getAuthBody());
            setGroups(res.data.groups || []);
        } catch (e) { console.error(e); }
    };

    const fetchNotes = async () => {
        try {
            const res = await api.post('/notes/get', getAuthBody());
            let data = res.data.notes || [];
            
            const mapped = data.map(n => {
                let lat = 52.23, lng = 21.01, color = '#3b82f6';
                if (Array.isArray(n.tags)) {
                    n.tags.forEach(t => {
                        if (t.startsWith('lat:')) lat = parseFloat(t.split(':')[1]);
                        if (t.startsWith('lng:')) lng = parseFloat(t.split(':')[1]);
                        if (t.startsWith('col:')) color = t.split(':')[1];
                    });
                }
                return { ...n, lat, lng, color };
            });
            setNotes(mapped);
        } catch (e) { console.error(e); }
    };

    const handleMapClick = (latlng) => {
        setEditMode(false);
        setNotePos(latlng);
        setForm({ title: '', content: '', color: '#3b82f6', group_id: '' });
        setFormVisible(true);
    };

    const handleEditStart = (note) => {
        setEditMode(true);
        setCurrentNoteId(note.id);
        setNotePos({ lat: note.lat, lng: note.lng });
        setForm({ title: note.title, content: note.content, color: note.color, group_id: note.group_id || '' });
        setFormVisible(true);
    };

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            const tags = [`lat:${notePos.lat}`, `lng:${notePos.lng}`, `col:${form.color}`, "geonotatka"];
            
            if (editMode) {
                await api.post('/notes/update', getAuthBody({
                    note_id: currentNoteId,
                    title: form.title,
                    content: form.content,
                    tags: tags,
                    group_id: form.group_id
                }));
            } else {
                await api.post('/notes/create', getAuthBody({
                    title: form.title,
                    content: form.content,
                    tags: tags,
                    group_id: form.group_id
                }));
            }
            setFormVisible(false);
            setNotePos(null);
            fetchNotes();
        } catch (e) { alert("Błąd zapisu! " + (e.response?.data?.detail || "")); }
    };

    const handleDelete = async (noteId) => {
        if (!confirm("Usunąć?")) return;
        try {
            await api.post('/notes/delete', getAuthBody({ note_id: noteId })); 
            fetchNotes();
        } catch (e) { alert("Błąd usuwania."); }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div className="relative h-full w-full flex overflow-hidden">
            {sidebarOpen && (
                <div className="w-80 bg-white shadow-xl z-[1000] overflow-y-auto border-r border-gray-200 flex flex-col h-full shrink-0">
                    <div className="bg-slate-800 text-white p-4 sticky top-0 z-10 shadow-md">
                        <div className="flex items-center gap-3 mb-3">
                            {user.picture ? <img src={user.picture} className="w-12 h-12 rounded-full border-2 border-slate-400 object-cover cursor-pointer" onClick={() => navigate('/profile')} onError={(e) => {e.target.style.display='none'}} /> : <div className="w-12 h-12 rounded-full bg-slate-600 flex items-center justify-center text-xl font-bold cursor-pointer" onClick={() => navigate('/profile')}>{user.name.charAt(0).toUpperCase()}</div>}
                            <div className="flex-1 min-w-0">
                                <h2 className="font-bold text-sm truncate">{user.name}</h2>
                                <div className="flex gap-2 mt-1">
                                    <button onClick={() => navigate('/profile')} className="text-xs text-blue-300 hover:text-white underline">Profil</button>
                                    <button onClick={() => navigate('/groups')} className="text-xs text-green-300 hover:text-white underline">Grupy</button>
                                </div>
                            </div>
                            <button onClick={() => setSidebarOpen(false)} className="self-start text-slate-400 hover:text-white">✕</button>
                        </div>
                        <div className="flex justify-between items-center text-xs text-slate-400 border-t border-slate-700 pt-2">
                            <span>Notatki: {notes.length}</span>
                            <button onClick={handleLogout} className="text-red-400 hover:text-red-300">Wyloguj</button>
                        </div>
                    </div>

                    <div className="p-2 flex-1 bg-gray-50">
                        {notes.map(note => (
                            <div key={note.id} className="bg-white border border-gray-200 rounded mb-2 p-3 hover:shadow-md transition relative group overflow-hidden">
                                <div className="absolute left-0 top-0 bottom-0 w-1.5" style={{ backgroundColor: note.color }}></div>
                                <div className="pl-2">
                                    <h3 className="font-bold text-slate-800 text-sm cursor-pointer hover:text-blue-600" onClick={() => handleEditStart(note)}>{note.title}</h3>
                                    <p className="text-xs text-gray-500 truncate mt-1">{note.content}</p>
                                    {note.group_name && <span className="text-[10px] bg-slate-100 text-slate-500 px-1 rounded mt-1 inline-block">Grupa: {note.group_name}</span>}
                                </div>
                                <div className="mt-2 flex gap-2 justify-end border-t border-gray-100 pt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button onClick={() => handleEditStart(note)} className="text-xs text-blue-600 font-bold hover:underline">EDYTUJ</button>
                                    <button onClick={() => handleDelete(note.id)} className="text-xs text-red-500 font-bold hover:underline">USUŃ</button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {!sidebarOpen && <button onClick={() => setSidebarOpen(true)} className="absolute top-4 left-4 z-[999] bg-white p-3 rounded-full shadow-lg font-bold hover:bg-gray-100 text-slate-800">☰</button>}

            <div className="flex-1 relative h-full">
                <MapContainer center={[52.23, 21.01]} zoom={6} className="h-full w-full" zoomControl={false}>
                    <ZoomControl position="topright" />
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    <MapClickHandler onMapClick={handleMapClick} />
                    {notes.map((note) => (
                        <Marker key={note.id} position={[note.lat, note.lng]} icon={getColoredIcon(note.color)}>
                            <Popup>
                                <div className="min-w-[180px]">
                                    <h3 className="font-bold border-b pb-1 mb-2">{note.title}</h3>
                                    <p className="mb-3 text-sm max-h-40 overflow-y-auto whitespace-pre-wrap">{note.content}</p>
                                    {note.group_name && <p className="text-xs text-gray-400 mb-2">👥 {note.group_name}</p>}
                                    <div className="flex gap-2">
                                        <button onClick={() => handleEditStart(note)} className="bg-blue-500 text-white text-xs px-2 py-1 rounded flex-1 hover:bg-blue-600">Edytuj</button>
                                        <button onClick={() => handleDelete(note.id)} className="bg-red-500 text-white text-xs px-2 py-1 rounded flex-1 hover:bg-red-600">Usuń</button>
                                    </div>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                    {formVisible && !editMode && notePos && <Marker position={notePos} icon={getColoredIcon(form.color)} opacity={0.6} />}
                </MapContainer>

                {formVisible && (
                    <div className="absolute top-16 right-16 z-[1000] bg-white p-5 rounded-lg shadow-2xl w-80 border border-gray-200 animate-slide-in">
                        <div className="flex justify-between items-center mb-4 border-b pb-2">
                            <h3 className="font-bold text-lg text-slate-700">{editMode ? '✏️ Edycja' : '📍 Nowa'}</h3>
                            <button onClick={()=>setFormVisible(false)} className="text-gray-400 hover:text-gray-600 text-xl font-bold">×</button>
                        </div>
                        <form onSubmit={handleSave} className="flex flex-col gap-3">
                            <input className="border p-2 rounded focus:ring-2 focus:ring-blue-200 outline-none" placeholder="Tytuł" required autoFocus value={form.title} onChange={e=>setForm({...form, title: e.target.value})} />
                            <textarea className="border p-2 rounded h-24 focus:ring-2 focus:ring-blue-200 outline-none resize-none" placeholder="Treść..." required value={form.content} onChange={e=>setForm({...form, content: e.target.value})} />
                            
                            <div className="flex flex-col gap-1">
                                <label className="text-xs font-bold text-gray-500">WIDOCZNOŚĆ</label>
                                <select className="border p-2 rounded bg-gray-50 text-sm" value={form.group_id} onChange={e=>setForm({...form, group_id: e.target.value})}>
                                    <option value="">🔒 Tylko dla mnie</option>
                                    {groups.map(g => (
                                        <option key={g.id} value={g.id}>👥 {g.name}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex items-center justify-between bg-gray-50 p-2 rounded border">
                                <span className="text-xs font-bold text-gray-500">KOLOR</span>
                                <input type="color" className="cursor-pointer w-8 h-8 rounded-full border-0 p-0 overflow-hidden" value={form.color} onChange={e=>setForm({...form, color: e.target.value})} />
                            </div>

                            <div className="flex gap-2 mt-2">
                                <button type="button" onClick={()=>setFormVisible(false)} className="bg-gray-100 text-gray-600 p-2 rounded flex-1 hover:bg-gray-200 font-medium">Anuluj</button>
                                <button className="bg-blue-600 text-white p-2 rounded flex-1 hover:bg-blue-700 font-bold shadow">{editMode ? 'Zapisz' : 'Dodaj'}</button>
                            </div>
                        </form>
                    </div>
                )}
            </div>
        </div>
    );
};
export default MapPage;