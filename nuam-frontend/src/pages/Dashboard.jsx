const Dashboard = () => {
    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium mb-2">Calificaciones Vigentes</h3>
                    <p className="text-3xl font-bold text-red-600">124</p>
                    <span className="text-green-500 text-xs font-medium">↑ 12% vs mes anterior</span>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium mb-2">Empresas Activas</h3>
                    <p className="text-3xl font-bold text-gray-600">45</p>
                    <span className="text-gray-400 text-xs font-medium">Total registradas</span>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h3 className="text-gray-500 text-sm font-medium mb-2">Auditorías Recientes</h3>
                    <p className="text-3xl font-bold text-red-500">8</p>
                    <span className="text-gray-400 text-xs font-medium">Últimos 7 días</span>
                </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Actividad Reciente</h2>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center p-3 hover:bg-gray-50 rounded-lg transition-colors">
                            <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center mr-4">
                                📝
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-800">Nueva calificación registrada</p>
                                <p className="text-xs text-gray-500">Hace {i} horas • Por Usuario Admin</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

