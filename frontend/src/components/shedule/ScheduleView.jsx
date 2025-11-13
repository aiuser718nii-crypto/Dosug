import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { scheduleService } from '../../services/api';
import ScheduleTable from './ScheduleTable';
import ConflictViewer from './ConflictViewer';
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
    if (!confirm('Активировать это расписание?')) return;
    
    try {
      await scheduleService.activate(id);
      toast.success('Расписание активировано');
      loadSchedule();
    } catch (error) {
      toast.error('Ошибка активации');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Удалить расписание?')) return;
    
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
      <div className="flex justify-center items-center h-64">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">{schedule.name}</h1>
          <p className="text-gray-500 mt-1">
            {schedule.semester} • {schedule.academic_year}
          </p>
          <div className="flex items-center space-x-4 mt-2">
            <span className={`px-3 py-1 text-sm rounded ${
              schedule.status === 'active'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {schedule.status === 'active' ? 'Активно' : 'Черновик'}
            </span>
            {schedule.fitness_score && (
              <span className="text-sm text-gray-500">
                Качество: {schedule.fitness_score.toFixed(1)}
              </span>
            )}
          </div>
        </div>

        <div className="flex space-x-2">
          {schedule.status !== 'active' && (
            <button
              onClick={handleActivate}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Активировать
            </button>
          )}
          
          <div className="relative group">
            <button
              disabled={exporting}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {exporting ? 'Экспорт...' : 'Экспорт'}
            </button>
            
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg hidden group-hover:block z-10">
              <button
                onClick={() => handleExport('group')}
                className="block w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                По группам
              </button>
              <button
                onClick={() => handleExport('teacher')}
                className="block w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                По преподавателям
              </button>
              <button
                onClick={() => handleExport('room')}
                className="block w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                По аудиториям
              </button>
              <button
                onClick={() => handleExport('consolidated')}
                className="block w-full text-left px-4 py-2 hover:bg-gray-100"
              >
                Сводное
              </button>
            </div>
          </div>

          <button
            onClick={handleDelete}
            className="px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50"
          >
            Удалить
          </button>
        </div>
      </div>

      {/* Конфликты */}
      {conflicts.length > 0 && (
        <ConflictViewer conflicts={conflicts} />
      )}

      {/* Расписание */}
      <ScheduleTable lessons={schedule.lessons} />
    </div>
  );
}