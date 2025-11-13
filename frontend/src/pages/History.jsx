import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { scheduleService } from '../services/api';
import toast from 'react-hot-toast';

export default function History() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      const data = await scheduleService.getAll();
      setSchedules(data);
    } catch (error) {
      toast.error('Ошибка загрузки расписаний');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">История расписаний</h1>
        <Link
          to="/generate"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Создать новое
        </Link>
      </div>

      {schedules.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          <p>Расписаний пока нет</p>
          <Link to="/generate" className="text-blue-600 hover:underline mt-2 inline-block">
            Создать первое расписание
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {schedules.map(schedule => (
            <Link
              key={schedule.id}
              to={`/schedules/${schedule.id}`}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-bold">{schedule.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {schedule.semester} • {schedule.academic_year}
                  </p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-sm text-gray-600">
                      📚 {schedule.lessons_count} занятий
                    </span>
                    {schedule.fitness_score && (
                      <span className="text-sm text-gray-600">
                        ⭐ Качество: {schedule.fitness_score.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <span className={`inline-block px-3 py-1 text-sm rounded ${
                    schedule.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {schedule.status === 'active' ? 'Активно' : 'Черновик'}
                  </span>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(schedule.created_at).toLocaleDateString('ru-RU')}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}