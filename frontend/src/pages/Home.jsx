import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { scheduleService } from '../services/api';

export default function Home() {
  const [stats, setStats] = useState({
    teachers: 0,
    rooms: 0,
    groups: 0,
    schedules: 0
  });
  const [recentSchedules, setRecentSchedules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const schedules = await scheduleService.getAll();
      setRecentSchedules(schedules.slice(0, 5));
      
      // Загрузка статистики (можно добавить отдельный endpoint)
      setStats({
        teachers: 0,
        rooms: 0,
        groups: 0,
        schedules: schedules.length
      });
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Генератор расписания
        </h1>
        <Link
          to="/generate"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
        >
          Создать расписание
        </Link>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Преподаватели"
          value={stats.teachers}
          icon="👨‍🏫"
          link="/teachers"
        />
        <StatCard
          title="Аудитории"
          value={stats.rooms}
          icon="🏫"
          link="/rooms"
        />
        <StatCard
          title="Группы"
          value={stats.groups}
          icon="👥"
          link="/groups"
        />
        <StatCard
          title="Расписания"
          value={stats.schedules}
          icon="📅"
          link="/history"
        />
      </div>

      {/* Последние расписания */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Последние расписания</h2>
        
        {loading ? (
          <div className="text-center py-8">
            <div className="spinner"></div>
            <p className="text-gray-500 mt-2">Загрузка...</p>
          </div>
        ) : recentSchedules.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>Расписаний пока нет</p>
            <Link to="/generate" className="text-blue-600 hover:underline mt-2 inline-block">
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

      {/* Быстрый старт */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-bold mb-3">🚀 Быстрый старт</h3>
        <ol className="list-decimal list-inside space-y-2 text-gray-700">
          <li>Добавьте <Link to="/teachers" className="text-blue-600 hover:underline">преподавателей</Link></li>
          <li>Добавьте <Link to="/rooms" className="text-blue-600 hover:underline">аудитории</Link></li>
          <li>Создайте <Link to="/subjects" className="text-blue-600 hover:underline">предметы</Link></li>
          <li>Добавьте <Link to="/groups" className="text-blue-600 hover:underline">группы</Link> и назначьте им предметы</li>
          <li>
            <Link to="/generate" className="text-blue-600 hover:underline">Сгенерируйте расписание</Link> 
            с помощью генетического алгоритма
          </li>
        </ol>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, link }) {
  return (
    <Link to={link} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </Link>
  );
}

function ScheduleItem({ schedule }) {
  return (
    <Link
      to={`/schedules/${schedule.id}`}
      className="block p-4 border rounded-lg hover:bg-gray-50 transition"
    >
      <div className="flex justify-between items-start">
        <div>
          <h4 className="font-semibold">{schedule.name}</h4>
          <p className="text-sm text-gray-500">
            {schedule.semester} • {schedule.academic_year}
          </p>
        </div>
        <div className="text-right">
          <span className={`inline-block px-2 py-1 text-xs rounded ${
            schedule.status === 'active' 
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {schedule.status === 'active' ? 'Активно' : 'Черновик'}
          </span>
          <p className="text-xs text-gray-500 mt-1">
            {schedule.lessons_count} занятий
          </p>
        </div>
      </div>
    </Link>
  );
}