import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { scheduleService } from '../services/api';

export default function Schedules() {
  const navigate = useNavigate();
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      const data = await scheduleService.getAll();
      setSchedules(data);
    } catch (error) {
      console.error('Ошибка загрузки расписаний:', error);
      alert('Не удалось загрузить расписания');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить это расписание?')) return;

    try {
      await scheduleService.delete(id);
      loadSchedules();
    } catch (error) {
      alert('Ошибка при удалении расписания');
    }
  };

  const handleExport = async (id) => {
    try {
      await scheduleService.export(id);
    } catch (error) {
      alert('Ошибка при экспорте');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="spinner mx-auto"></div>
          <p className="text-gray-500 mt-2">Загрузка расписаний...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Расписания</h1>
          <p className="text-gray-600 mt-1">Список всех созданных расписаний</p>
        </div>
        <button
          onClick={() => navigate('/generate-semester')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <span>🚀</span>
          Создать расписание
        </button>
      </div>

      {schedules.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">📅</div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            Расписаний пока нет
          </h2>
          <p className="text-gray-500 mb-6">
            Создайте первое расписание с помощью генератора
          </p>
          <button
            onClick={() => navigate('/generate-semester')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
          >
            🚀 Создать расписание
          </button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {schedules.map((schedule) => (
            <ScheduleCard
              key={schedule.id}
              schedule={schedule}
              onView={() => navigate(`/schedules/${schedule.id}`)}
              onExport={() => handleExport(schedule.id)}
              onDelete={() => handleDelete(schedule.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Компонент карточки расписания
function ScheduleCard({ schedule, onView, onExport, onDelete }) {
  const getStatusColor = (status) => {
    const colors = {
      draft: 'bg-gray-100 text-gray-800',
      active: 'bg-green-100 text-green-800',
      archived: 'bg-orange-100 text-orange-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusName = (status) => {
    const names = {
      draft: 'Черновик',
      active: 'Активно',
      archived: 'Архив',
    };
    return names[status] || status;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition overflow-hidden">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-3 text-white">
        <h3 className="font-semibold text-lg truncate">{schedule.name}</h3>
        <div className="flex items-center gap-2 mt-1 text-sm text-blue-100">
          {schedule.semester && <span>📚 {schedule.semester}</span>}
          {schedule.academic_year && <span>• {schedule.academic_year}</span>}
        </div>
      </div>

      {/* Содержимое */}
      <div className="p-4">
        {/* Статус */}
        <div className="flex items-center justify-between mb-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(
              schedule.status
            )}`}
          >
            {getStatusName(schedule.status)}
          </span>
          {schedule.created_at && (
            <span className="text-xs text-gray-500">
              {formatDate(schedule.created_at)}
            </span>
          )}
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div className="text-center p-2 bg-blue-50 rounded">
            <p className="text-lg font-bold text-blue-900">
              {schedule.lessons_count || 0}
            </p>
            <p className="text-xs text-blue-600">Занятий</p>
          </div>
          <div className="text-center p-2 bg-green-50 rounded">
            <p className="text-lg font-bold text-green-900">
              {schedule.fitness_score
                ? `${(schedule.fitness_score * 100).toFixed(0)}%`
                : '—'}
            </p>
            <p className="text-xs text-green-600">Качество</p>
          </div>
          <div className="text-center p-2 bg-red-50 rounded">
            <p className="text-lg font-bold text-red-900">
              {schedule.conflicts_count || 0}
            </p>
            <p className="text-xs text-red-600">Конфликтов</p>
          </div>
        </div>

        {/* Дополнительная информация */}
        {schedule.generation_method && (
          <div className="mb-3 text-xs text-gray-600">
            <span className="font-medium">Метод:</span>{' '}
            {schedule.generation_method === 'genetic_extended'
              ? 'Генетический (расширенный)'
              : schedule.generation_method}
          </div>
        )}

        {schedule.generation_time && (
          <div className="mb-3 text-xs text-gray-600">
            <span className="font-medium">Время генерации:</span>{' '}
            {schedule.generation_time.toFixed(2)} сек
          </div>
        )}

        {/* Действия */}
        <div className="grid grid-cols-3 gap-2 mt-4">
          <button
            onClick={onView}
            className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
            title="Просмотреть"
          >
            👁️
          </button>
          <button
            onClick={onExport}
            className="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium"
            title="Экспорт в Excel"
          >
            📥
          </button>
          <button
            onClick={onDelete}
            className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
            title="Удалить"
          >
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
}