import { Outlet, Link, useLocation } from 'react-router-dom';

export default function Layout() {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };
  
  const navItems = [
    { path: '/', label: '🏠 Главная', exact: true },
    { path: '/teachers', label: '👨‍🏫 Преподаватели' },
    { path: '/rooms', label: '🏫 Аудитории' },
    { path: '/subjects', label: '📚 Предметы' },
    { path: '/groups', label: '👥 Группы' },
    { path: '/semesters', label: '📅 Семестры' },
    { path: '/lesson-types', label: '📝 Типы занятий' },
    { path: '/constraints', label: '🔗 Ограничения' },
    { path: '/generate-semester', label: '🚀 Генерация' },
    { path: '/schedules', label: '📊 Расписания' },
  ];
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Навигация */}
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-bold text-blue-600">
                📚 Расписание
              </Link>
            </div>
            <div className="hidden md:flex space-x-1">
              {navItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                    (item.exact ? location.pathname === item.path : isActive(item.path))
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>
      
      {/* Контент */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}