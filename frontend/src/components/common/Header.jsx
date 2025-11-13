import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="flex items-center space-x-3">
            <div className="text-3xl">📅</div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Генератор расписания
              </h1>
              <p className="text-xs text-gray-500">
                Генетический алгоритм
              </p>
            </div>
          </Link>

          <nav className="flex space-x-6">
            <Link
              to="/"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Главная
            </Link>
            <Link
              to="/generate"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              Генерация
            </Link>
            <Link
              to="/history"
              className="text-gray-700 hover:text-blue-600 transition"
            >
              История
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}