import { useState } from 'react';

export default function ScheduleTable({ lessons }) {
  const [viewMode, setViewMode] = useState('group'); // group, teacher, room
  const [selectedEntity, setSelectedEntity] = useState(null);

  const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];
  const times = [
    '08:00-09:30', '09:40-11:10', '11:20-12:50',
    '13:30-15:00', '15:10-16:40', '16:50-18:20', '18:30-20:00'
  ];

  // Группируем занятия по выбранному режиму
  const entities = [...new Set(lessons.map(l => l[viewMode]))].sort();
  
  const currentLessons = selectedEntity
    ? lessons.filter(l => l[viewMode] === selectedEntity)
    : lessons;

  // Создаем матрицу расписания
  const matrix = {};
  currentLessons.forEach(lesson => {
    const key = `${lesson.day}-${lesson.time_slot}`;
    if (!matrix[key]) matrix[key] = [];
    matrix[key].push(lesson);
  });

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Фильтры */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium">Вид:</label>
          <select
            value={viewMode}
            onChange={(e) => {
              setViewMode(e.target.value);
              setSelectedEntity(null);
            }}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="group">По группам</option>
            <option value="teacher">По преподавателям</option>
            <option value="room">По аудиториям</option>
          </select>

          {entities.length > 0 && (
            <>
              <label className="text-sm font-medium">Фильтр:</label>
              <select
                value={selectedEntity || ''}
                onChange={(e) => setSelectedEntity(e.target.value || null)}
                className="px-3 py-2 border rounded-lg"
              >
                <option value="">Все</option>
                {entities.map(entity => (
                  <option key={entity} value={entity}>{entity}</option>
                ))}
              </select>
            </>
          )}
        </div>
      </div>

      {/* Таблица */}
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700 w-32">
                Время
              </th>
              {days.map(day => (
                <th key={day} className="px-4 py-3 text-center text-sm font-medium text-gray-700">
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {times.map((time, timeIdx) => (
              <tr key={timeIdx} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-700 bg-gray-50">
                  {time}
                </td>
                {days.map((day, dayIdx) => {
                  const key = `${dayIdx}-${timeIdx}`;
                  const cellLessons = matrix[key] || [];

                  return (
                    <td key={dayIdx} className="px-2 py-2 align-top">
                      {cellLessons.length > 0 ? (
                        <div className="space-y-1">
                          {cellLessons.map((lesson, idx) => (
                            <div
                              key={idx}
                              className={`p-2 rounded text-xs ${
                                cellLessons.length > 1
                                  ? 'bg-red-50 border border-red-200'
                                  : 'bg-blue-50 border border-blue-200'
                              }`}
                            >
                              <div className="font-semibold text-gray-900">
                                {lesson.subject}
                              </div>
                              <div className="text-gray-600 mt-1">
                                {lesson.teacher}
                              </div>
                              <div className="text-gray-500">
                                {lesson.group} • ауд. {lesson.room}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="h-20"></div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Легенда */}
      <div className="p-4 border-t bg-gray-50 text-xs text-gray-600">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-50 border border-blue-200 rounded mr-2"></div>
            Нормальное занятие
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-50 border border-red-200 rounded mr-2"></div>
            Конфликт (несколько занятий в одно время)
          </div>
        </div>
      </div>
    </div>
  );
}