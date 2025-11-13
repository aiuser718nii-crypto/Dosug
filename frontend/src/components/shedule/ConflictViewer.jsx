export default function ConflictViewer({ conflicts }) {
  const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница'];
  const times = [
    '08:00-09:30', '09:40-11:10', '11:20-12:50',
    '13:30-15:00', '15:10-16:40', '16:50-18:20', '18:30-20:00'
  ];

  if (conflicts.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <span className="text-2xl mr-3">✅</span>
          <div>
            <h3 className="font-semibold text-green-800">Конфликтов не обнаружено</h3>
            <p className="text-sm text-green-700">Расписание составлено корректно</p>
          </div>
        </div>
      </div>
    );
  }

  const conflictsByType = {
    teacher: conflicts.filter(c => c.type === 'teacher'),
    room: conflicts.filter(c => c.type === 'room'),
    group: conflicts.filter(c => c.type === 'group')
  };

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <div className="flex items-start mb-4">
        <span className="text-2xl mr-3">⚠️</span>
        <div>
          <h3 className="font-semibold text-red-800">
            Обнаружено конфликтов: {conflicts.length}
          </h3>
          <p className="text-sm text-red-700">
            Расписание требует корректировки
          </p>
        </div>
      </div>

      <div className="space-y-4 mt-4">
        {conflictsByType.teacher.length > 0 && (
          <div>
            <h4 className="font-medium text-red-800 mb-2">
              Конфликты преподавателей ({conflictsByType.teacher.length})
            </h4>
            <ul className="space-y-1">
              {conflictsByType.teacher.map((conflict, idx) => (
                <li key={idx} className="text-sm text-red-700">
                  • {conflict.message}
                </li>
              ))}
            </ul>
          </div>
        )}

        {conflictsByType.room.length > 0 && (
          <div>
            <h4 className="font-medium text-red-800 mb-2">
              Конфликты аудиторий ({conflictsByType.room.length})
            </h4>
            <ul className="space-y-1">
              {conflictsByType.room.map((conflict, idx) => (
                <li key={idx} className="text-sm text-red-700">
                  • {conflict.message}
                </li>
              ))}
            </ul>
          </div>
        )}

        {conflictsByType.group.length > 0 && (
          <div>
            <h4 className="font-medium text-red-800 mb-2">
              Конфликты групп ({conflictsByType.group.length})
            </h4>
            <ul className="space-y-1">
              {conflictsByType.group.map((conflict, idx) => (
                <li key={idx} className="text-sm text-red-700">
                  • {conflict.message}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}