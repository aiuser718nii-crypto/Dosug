import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scheduleService } from '../services/api';
import ScheduleTable from '../components/shedule/ScheduleTable';
import ConflictViewer from '../components/shedule/ConflictViewer';
import toast from 'react-hot-toast';

export default function ScheduleView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [schedule, setSchedule] = useState(null);
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadSchedule();
    loadConflicts();
  }, [id]);

  const loadSchedule = async () => {
    try {
      const data = await scheduleService.getById(id);
      setSchedule(data);
    } catch (error) {
      toast.error('Ошибка загрузки расписания');
      navigate('/history');
    } finally {
      setLoading(false);
    }
  };

  const loadConflicts = async () => {
    try {
      const data = await scheduleService.getConflicts(id);
      setConflicts(data.conflicts);
    } catch (error) {
      console.error('Ошибка загрузки конфликтов:', error);
    }
  };

  const handleExport = async (type) => {
    try {
      setExporting(true);
      await scheduleService.export(id, type);
      toast.success('Файл загружен');
    } catch (error) {
      toast.error('Ошибка экспорта');
    } finally {
      setExporting(false);
    }
  };

  const handleActivate = async () => {
    if (!confirm('Активировать это расписание? Другие активные расписания будут деактивированы.')) {
      return;
    }
    
    try {
      await scheduleService.activate(id);
      toast.success('Расписание активировано');
      loadSchedule();
    } catch (error) {
      toast.error('Ошибка активации');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Удалить расписание? Это действие нельзя отменить.')) {
      return;
    }
    
    try {
      await scheduleService.delete(id);
      toast.success('Расписание удалено');
      navigate('/history');
    } catch (error) {
      toast.error('Ошибка удаления');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!schedule) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Расписание не найдено</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Шапка */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h1 className="text-3xl font-bold">{schedule.name}</h1>
            <div className="flex items-center space-x-4 mt-3">
              <span className="text-gray-600">
                📅 {schedule.semester}
              </span>
              <span className="text-gray-600">
                🗓️ {schedule.academic_year}
              </span>
              <span className={`px-3 py-1 text-sm rounded ${
                schedule.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : schedule.status === 'draft'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {schedule.status === 'active' ? 'Активно' : schedule.status === 'draft' ? 'Черновик' : 'Архив'}
              </span>
            </div>
            <div className="flex items-center space-x-6 mt-4 text-sm text-gray-600">
              <span>📚 Занятий: {schedule.lessons_count}</span>
              {schedule.fitness_score && (
                <span>⭐ Качество: {schedule.fitness_score.toFixed(2)}</span>
              )}
              {schedule.generation_method && (
                <span>🧬 Метод: {schedule.generation_method}</span>
              )}
              {schedule.generation_time && (
                <span>⏱️ Время генерации: {schedule.generation_time.toFixed(2)}с</span>
              )}
            </div>
          </div>

          {/* Кнопки действий */}
          <div className="flex space-x-2">
            {schedule.status !== 'active' && (
              <button
                onClick={handleActivate}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <span>✓</span>
                <span>Активировать</span>
              </button>
            )}
            
            <div className="relative group">
              <button
                disabled={exporting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
              >
                <span>📥</span>
                <span>{exporting ? 'Экспорт...' : 'Экспорт'}</span>
              </button>
              
              {!exporting && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg hidden group-hover:block z-10 border">
                  <button
                    onClick={() => handleExport('group')}
                    className="block w-full text-left px-4 py-3 hover:bg-gray-50 transition"
                  >
                    <div className="font-medium">По группам</div>
                    <div className="text-xs text-gray-500">Отдельный лист для каждой группы</div>
                  </button>
                  <button
                    onClick={() => handleExport('teacher')}
                    className="block w-full text-left px-4 py-3 hover:bg-gray-50 transition border-t"
                  >
                    <div className="font-medium">По преподавателям</div>
                    <div className="text-xs text-gray-500">Отдельный лист для каждого преподавателя</div>
                  </button>
                  <button
                    onClick={() => handleExport('room')}
                    className="block w-full text-left px-4 py-3 hover:bg-gray-50 transition border-t"
                  >
                    <div className="font-medium">По аудиториям</div>
                    <div className="text-xs text-gray-500">Загруженность аудиторий</div>
                  </button>
                  <button
                    onClick={() => handleExport('consolidated')}
                    className="block w-full text-left px-4 py-3 hover:bg-gray-50 transition border-t"
                  >
                    <div className="font-medium">Сводное</div>
                    <div className="text-xs text-gray-500">Все занятия в одной таблице</div>
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={handleDelete}
              className="px-4 py-2 border-2 border-red-600 text-red-600 rounded-lg hover:bg-red-50 flex items-center space-x-2"
            >
              <span>🗑️</span>
              <span>Удалить</span>
            </button>
          </div>
        </div>
      </div>

      {/* Конфликты */}
      {conflicts && conflicts.length > 0 && (
        <ConflictViewer conflicts={conflicts} />
      )}

      {/* Таблица расписания */}
      {schedule.lessons && schedule.lessons.length > 0 ? (
        <ScheduleTable lessons={schedule.lessons} />
      ) : (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            Расписание пусто
          </h3>
          <p className="text-gray-500">
            В этом расписании нет занятий
          </p>
        </div>
      )}
    </div>
  );
}