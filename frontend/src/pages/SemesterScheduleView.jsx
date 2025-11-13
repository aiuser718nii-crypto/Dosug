import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { semesterScheduleService } from '../services/semesterApi';
import { scheduleService } from '../services/api';

export default function SemesterScheduleView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [schedule, setSchedule] = useState(null);
  const [selectedWeek, setSelectedWeek] = useState(1);
  const [weekData, setWeekData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('week'); // 'week' или 'overview'
  
  useEffect(() => {
    loadSchedule();
  }, [id]);
  
  useEffect(() => {
    if (schedule) {
      loadWeekData(selectedWeek);
    }
  }, [selectedWeek, schedule]);
  
  const loadSchedule = async () => {
    try {
      setLoading(true);
      const data = await semesterScheduleService.getExtended(id);
      setSchedule(data);
    } catch (error) {
      console.error('Ошибка загрузки расписания:', error);
      alert('Не удалось загрузить расписание');
    } finally {
      setLoading(false);
    }
  };
  
  const loadWeekData = async (weekNumber) => {
    try {
      const data = await semesterScheduleService.getWeek(id, weekNumber);
      setWeekData(data);
    } catch (error) {
      console.error('Ошибка загрузки недели:', error);
    }
  };
  
  const handleExport = async () => {
    try {
      await scheduleService.export(id);
    } catch (error) {
      alert('Ошибка экспорта');
    }
  };
  
  const handleDelete = async () => {
    if (!window.confirm('Удалить это расписание?')) return;
    
    try {
      await scheduleService.delete(id);
      navigate('/schedules');
    } catch (error) {
      alert('Ошибка удаления');
    }
  };
  
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="spinner mx-auto"></div>
          <p className="text-gray-500 mt-2">Загрузка расписания...</p>
        </div>
      </div>
    );
  }
  
  if (!schedule) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-red-600">Расписание не найдено</p>
          <button
            onClick={() => navigate('/schedules')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Назад к списку
          </button>
        </div>
      </div>
    );
  }
  
  const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];
  const timeSlots = [
    '08:00-09:30',
    '09:40-11:10',
    '11:20-12:50',
    '13:30-15:00',
    '15:10-16:40',
    '16:50-18:20',
    '18:30-20:00'
  ];
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Шапка */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-start">
            <div>
              <button
                onClick={() => navigate('/schedules')}
                className="text-blue-600 hover:text-blue-800 mb-2 flex items-center gap-1"
              >
                ← Назад к списку
              </button>
              <h1 className="text-2xl font-bold text-gray-900">{schedule.name}</h1>
              <p className="text-gray-600 mt-1">
                Недель: {schedule.weeks?.length || 0}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                📥 Экспорт Excel
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                🗑️ Удалить
              </button>
            </div>
          </div>
          
          {/* Статистика */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="bg-blue-50 rounded-lg p-3">
              <p className="text-sm text-blue-600">Качество</p>
              <p className="text-2xl font-bold text-blue-900">
                {schedule.fitness_score ? `${(schedule.fitness_score * 100).toFixed(1)}%` : '—'}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <p className="text-sm text-green-600">Занятий</p>
              <p className="text-2xl font-bold text-green-900">
                {schedule.weeks?.reduce((sum, w) => sum + w.lessons.length, 0) || 0}
              </p>
            </div>
            <div className="bg-red-50 rounded-lg p-3">
              <p className="text-sm text-red-600">Конфликтов</p>
              <p className="text-2xl font-bold text-red-900">
                {schedule.conflicts_count || 0}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Переключатель вида */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="bg-white rounded-lg shadow p-2 inline-flex gap-2">
          <button
            onClick={() => setView('week')}
            className={`px-4 py-2 rounded ${
              view === 'week'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📅 По неделям
          </button>
          <button
            onClick={() => setView('overview')}
            className={`px-4 py-2 rounded ${
              view === 'overview'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📊 Обзор
          </button>
        </div>
      </div>
      
      {/* Контент */}
      <div className="max-w-7xl mx-auto px-4 pb-8">
        {view === 'week' ? (
          <WeekView
            schedule={schedule}
            selectedWeek={selectedWeek}
            onWeekChange={setSelectedWeek}
            weekData={weekData}
            days={days}
            timeSlots={timeSlots}
          />
        ) : (
          <OverviewView schedule={schedule} />
        )}
      </div>
    </div>
  );
}

// Компонент просмотра недели
function WeekView({ schedule, selectedWeek, onWeekChange, weekData, days, timeSlots }) {
  if (!weekData) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="spinner mx-auto"></div>
        <p className="text-gray-500 mt-2">Загрузка недели...</p>
      </div>
    );
  }
  
  return (
    <>
      {/* Селектор недель */}
      <div className="bg-white rounded-lg shadow p-4 mb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => onWeekChange(Math.max(1, selectedWeek - 1))}
            disabled={selectedWeek === 1}
            className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            ← Предыдущая
          </button>
          
          <div className="flex-1">
            <select
              value={selectedWeek}
              onChange={(e) => onWeekChange(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              {schedule.weeks?.map(week => (
                <option key={week.week_number} value={week.week_number}>
                  Неделя {week.week_number} ({week.start_date} — {week.end_date})
                </option>
              ))}
            </select>
          </div>
          
          <button
            onClick={() => onWeekChange(Math.min(schedule.weeks.length, selectedWeek + 1))}
            disabled={selectedWeek === schedule.weeks.length}
            className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
          >
            Следующая →
          </button>
        </div>
      </div>
      
      {/* Таблица расписания */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 sticky left-0 bg-gray-50 z-10">
                  Время
                </th>
                {days.map((day, idx) => (
                  <th
                    key={idx}
                    className="px-4 py-3 text-left text-sm font-semibold text-gray-700 min-w-[200px]"
                  >
                    {day}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {timeSlots.map((time, slotIdx) => (
                <tr key={slotIdx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900 sticky left-0 bg-white">
                    {time}
                  </td>
                  {days.map((_, dayIdx) => {
                    const lessons = weekData.timetable?.[dayIdx]?.[slotIdx] || [];
                    
                    return (
                      <td key={dayIdx} className="px-4 py-3 align-top">
                        {lessons.length > 0 ? (
                          <div className="space-y-2">
                            {lessons.map((lesson, idx) => (
                              <LessonCard key={idx} lesson={lesson} />
                            ))}
                          </div>
                        ) : (
                          <div className="text-center text-gray-300 text-sm">—</div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

// Карточка занятия
function LessonCard({ lesson }) {
  const lessonTypeColors = {
    lecture: 'bg-blue-100 border-blue-300 text-blue-900',
    seminar: 'bg-green-100 border-green-300 text-green-900',
    lab: 'bg-purple-100 border-purple-300 text-purple-900',
    practice: 'bg-orange-100 border-orange-300 text-orange-900',
    field_trip: 'bg-red-100 border-red-300 text-red-900',
    training_center: 'bg-pink-100 border-pink-300 text-pink-900',
    production_visit: 'bg-yellow-100 border-yellow-300 text-yellow-900',
    exercises: 'bg-red-100 border-red-300 text-red-900',
    individual: 'bg-indigo-100 border-indigo-300 text-indigo-900',
  };
  
  const colorClass = lessonTypeColors[lesson.lesson_type?.code] || 'bg-gray-100 border-gray-300 text-gray-900';
  
  return (
    <div
      className={`p-2 rounded border-l-4 text-xs ${colorClass}`}
      style={{ borderLeftColor: lesson.lesson_type?.color }}
    >
      <div className="font-semibold mb-1">{lesson.subject}</div>
      <div className="text-opacity-80 mb-1">
        <span className="inline-block px-2 py-0.5 bg-white bg-opacity-50 rounded text-xs">
          {lesson.lesson_type?.name || 'Занятие'}
        </span>
      </div>
      <div className="space-y-0.5">
        <div>👥 {lesson.group}</div>
        <div>👨‍🏫 {lesson.teacher}</div>
        <div>🏫 {lesson.room}</div>
      </div>
      {lesson.is_online && (
        <div className="mt-1 text-xs">💻 Онлайн</div>
      )}
      {lesson.location && (
        <div className="mt-1 text-xs">📍 {lesson.location}</div>
      )}
    </div>
  );
}

// Компонент обзора
function OverviewView({ schedule }) {
  const totalLessons = schedule.weeks?.reduce((sum, w) => sum + w.lessons.length, 0) || 0;
  
  // Подсчёт по типам занятий
  const lessonTypeStats = {};
  schedule.weeks?.forEach(week => {
    week.lessons.forEach(lesson => {
      const typeName = lesson.lesson_type?.name || 'Неизвестно';
      lessonTypeStats[typeName] = (lessonTypeStats[typeName] || 0) + 1;
    });
  });
  
  return (
    <div className="space-y-6">
      {/* Общая статистика */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Общая статистика</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded">
            <p className="text-3xl font-bold text-gray-900">{schedule.weeks?.length || 0}</p>
            <p className="text-sm text-gray-600">Недель</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded">
            <p className="text-3xl font-bold text-gray-900">{totalLessons}</p>
            <p className="text-sm text-gray-600">Всего занятий</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded">
            <p className="text-3xl font-bold text-gray-900">
              {totalLessons && schedule.weeks ? Math.round(totalLessons / schedule.weeks.length) : 0}
            </p>
            <p className="text-sm text-gray-600">Среднее в неделю</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded">
            <p className="text-3xl font-bold text-gray-900">
              {schedule.fitness_score ? `${(schedule.fitness_score * 100).toFixed(0)}%` : '—'}
            </p>
            <p className="text-sm text-gray-600">Качество</p>
          </div>
        </div>
      </div>
      
      {/* По типам занятий */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Распределение по типам занятий</h2>
        <div className="space-y-3">
          {Object.entries(lessonTypeStats)
            .sort((a, b) => b[1] - a[1])
            .map(([type, count]) => (
              <div key={type} className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">{type}</span>
                    <span className="text-sm text-gray-600">{count} занятий</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(count / totalLessons) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </div>
      
      {/* График по неделям */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Занятий по неделям</h2>
        <div className="flex items-end gap-2 h-48">
          {schedule.weeks?.map(week => {
            const maxLessons = Math.max(...schedule.weeks.map(w => w.lessons.length));
            const height = (week.lessons.length / maxLessons) * 100;
            
            return (
              <div
                key={week.week_number}
                className="flex-1 bg-blue-500 rounded-t hover:bg-blue-600 transition relative group"
                style={{ height: `${height}%` }}
              >
                <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                  Неделя {week.week_number}: {week.lessons.length} занятий
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-600">
          <span>Неделя 1</span>
          <span>Неделя {schedule.weeks?.length || 0}</span>
        </div>
      </div>
    </div>
  );
}