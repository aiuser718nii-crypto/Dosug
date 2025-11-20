// frontend/src/pages/Home.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { scheduleService } from '../services/api';
import { statsService } from '../services/api';
import toast from 'react-hot-toast';

export default function Home() {
  const [stats, setStats] = useState({
    teachers: 0,
    rooms: 0,
    groups: 0,
    subjects: 0,
    schedules: 0,
    total_lessons: 0
  });
  const [recentSchedules, setRecentSchedules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

const loadData = async () => {
  try {
    setLoading(true);
    
    // Загружаем статистику
    console.log('Загрузка статистики...');
    const statsData = await statsService.getDashboard();
    console.log('Статистика загружена:', statsData);
    setStats(statsData);
    
    // Загружаем последние расписания
    console.log('Загрузка расписаний...');
    const schedules = await scheduleService.getAll();
    console.log('Расписания загружены:', schedules);
    
    // Проверяем первое расписание
    if (schedules.length > 0) {
      console.log('Первое расписание:', schedules[0]);
      console.log('lessons_count:', schedules[0].lessons_count);
    }
    
    setRecentSchedules(schedules.slice(0, 5));
    
  } catch (error) {
    console.error('Ошибка загрузки данных:', error);
    toast.error('Ошибка загрузки данных');
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Генератор расписания
          </h1>
          <p className="text-gray-500 mt-1">
            Автоматическое создание расписания занятий
          </p>
        </div>
        <Link
          to="/generate"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
        >
          <span>✨</span>
          <span>Создать расписание</span>
        </Link>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Преподаватели"
          value={stats.teachers}
          icon="👨‍🏫"
          link="/teachers"
          color="blue"
        />
        <StatCard
          title="Аудитории"
          value={stats.rooms}
          icon="🏫"
          link="/rooms"
          color="green"
        />
        <StatCard
          title="Группы"
          value={stats.groups}
          icon="👥"
          link="/groups"
          color="purple"
        />
        <StatCard
          title="Предметы"
          value={stats.subjects}
          icon="📚"
          link="/subjects"
          color="orange"
        />
      </div>

      {/* Дополнительная статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Всего расписаний</p>
              <p className="text-3xl font-bold mt-1">{stats.schedules}</p>
            </div>
            <div className="text-4xl opacity-50">📅</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Активных расписаний</p>
              <p className="text-3xl font-bold mt-1">{stats.active_schedules || 0}</p>
            </div>
            <div className="text-4xl opacity-50">✅</div>
          </div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Всего занятий</p>
              <p className="text-3xl font-bold mt-1">{stats.total_lessons || 0}</p>
            </div>
            <div className="text-4xl opacity-50">📖</div>
          </div>
        </div>
      </div>

      {/* Последние расписания */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Последние расписания</h2>
            <Link 
              to="/history" 
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Показать все →
            </Link>
          </div>
        </div>
        
        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="spinner mx-auto"></div>
              <p className="text-gray-500 mt-2">Загрузка...</p>
            </div>
          ) : recentSchedules.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📅</div>
              <p className="text-gray-500 mb-4">Расписаний пока нет</p>
              <Link 
                to="/generate" 
                className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Создать первое расписание
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentSchedules.map(schedule => (
                <ScheduleItem key={schedule.id} schedule={schedule} />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Быстрый старт */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow p-6 border border-blue-100">
        <div className="flex items-start gap-4">
          <div className="text-4xl">🚀</div>
          <div className="flex-1">
            <h3 className="text-lg font-bold mb-3 text-gray-900">Быстрый старт</h3>
            <ol className="list-decimal list-inside space-y-2 text-gray-700">
              <li>
                Добавьте <Link to="/teachers" className="text-blue-600 hover:underline font-medium">преподавателей</Link> 
                {stats.teachers > 0 && <span className="text-green-600 ml-2">✓ {stats.teachers}</span>}
              </li>
              <li>
                Добавьте <Link to="/rooms" className="text-blue-600 hover:underline font-medium">аудитории</Link>
                {stats.rooms > 0 && <span className="text-green-600 ml-2">✓ {stats.rooms}</span>}
              </li>
              <li>
                Создайте <Link to="/subjects" className="text-blue-600 hover:underline font-medium">предметы</Link>
                {stats.subjects > 0 && <span className="text-green-600 ml-2">✓ {stats.subjects}</span>}
              </li>
              <li>
                Добавьте <Link to="/groups" className="text-blue-600 hover:underline font-medium">группы</Link> и назначьте им предметы
                {stats.groups > 0 && <span className="text-green-600 ml-2">✓ {stats.groups}</span>}
              </li>
              <li>
                <Link to="/generate" className="text-blue-600 hover:underline font-medium">Сгенерируйте расписание</Link> 
                {' '}с помощью CSP алгоритма
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, link, color = 'blue' }) {
  const colorClasses = {
    blue: 'hover:border-blue-500 hover:shadow-blue-100',
    green: 'hover:border-green-500 hover:shadow-green-100',
    purple: 'hover:border-purple-500 hover:shadow-purple-100',
    orange: 'hover:border-orange-500 hover:shadow-orange-100'
  };

  return (
    <Link 
      to={link} 
      className={`bg-white rounded-lg shadow border-2 border-transparent p-6 hover:shadow-lg transition-all ${colorClasses[color]}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold mt-2 text-gray-900">{value}</p>
        </div>
        <div className="text-5xl opacity-80">{icon}</div>
      </div>
    </Link>
  );
}

function ScheduleItem({ schedule }) {
  // Форматирование даты
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('ru-RU', { 
        day: 'numeric', 
        month: 'short',
        year: 'numeric'
      });
    } catch (e) {
      return '';
    }
  };

  // Отладка
  console.log('Rendering schedule:', schedule.id, 'lessons_count:', schedule.lessons_count);

  return (
    <Link
      to={`/schedules/${schedule.id}`}
      className="block p-4 border-2 border-gray-100 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h4 className="font-semibold text-gray-900">{schedule.name}</h4>
            <span className={`inline-block px-2 py-0.5 text-xs font-medium rounded ${
              schedule.status === 'active' 
                ? 'bg-green-100 text-green-700 border border-green-300'
                : schedule.status === 'draft'
                ? 'bg-yellow-100 text-yellow-700 border border-yellow-300'
                : 'bg-gray-100 text-gray-700 border border-gray-300'
            }`}>
              {schedule.status === 'active' ? '✓ Активно' : 
               schedule.status === 'draft' ? '📝 Черновик' : 'Архив'}
            </span>
          </div>
          
          <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span>📅 {schedule.semester || 'Семестр не указан'}</span>
            <span>📚 {schedule.academic_year || 'Год не указан'}</span>
            {schedule.created_at && (
              <span>🕐 {formatDate(schedule.created_at)}</span>
            )}
          </div>
        </div>
        
        <div className="text-right ml-4">
          <div className="flex items-center gap-2 text-sm">
            {/* УЛУЧШЕННАЯ ПРОВЕРКА */}
            {(schedule.lessons_count !== undefined && schedule.lessons_count !== null) ? (
              <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
                {schedule.lessons_count} {schedule.lessons_count === 1 ? 'занятие' : 'занятий'}
              </div>
            ) : (
              <div className="bg-gray-100 text-gray-500 px-3 py-1 rounded-full font-medium text-xs">
                Загрузка...
              </div>
            )}
            
            {schedule.fitness_score !== undefined && schedule.fitness_score !== null && (
              <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-medium">
                {(schedule.fitness_score * 100).toFixed(0)}%
              </div>
            )}
          </div>
          
          {schedule.conflicts_count > 0 && (
            <p className="text-xs text-red-600 mt-1">
              ⚠️ {schedule.conflicts_count} {schedule.conflicts_count === 1 ? 'конфликт' : 'конфликтов'}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}