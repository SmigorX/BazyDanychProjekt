import { Link, useNavigate } from 'react-router-dom';

const Layout = ({ children }) => {
    const navigate = useNavigate();
    const token = localStorage.getItem('token');

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <div className="flex flex-col h-screen">
            <nav className="bg-slate-800 text-white p-4 flex justify-between items-center z-[2000]">
                <div className="font-bold text-xl">GeoNotatki</div>
                <div className="flex gap-4">
                    {token ? (
                        <>
                            <Link to="/" className="hover:text-blue-300">Mapa</Link>
                            <button onClick={handleLogout} className="bg-red-500 px-3 py-1 rounded hover:bg-red-600">Wyloguj</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="hover:text-blue-300">Logowanie</Link>
                            <Link to="/register" className="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700">Rejestracja</Link>
                        </>
                    )}
                </div>
            </nav>
            <main className="flex-1 relative overflow-hidden">{children}</main>
        </div>
    );
};
export default Layout;