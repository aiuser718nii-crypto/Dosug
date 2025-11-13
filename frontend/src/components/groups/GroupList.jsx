export default function GroupList({ groups, loading, onEdit, onDelete }) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="spinner mx-auto"></div>
        <p className="text-gray-500 mt-2">Загрузка...</p>
      </div>
    );
  }

  if (groups.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-6xl mb-4">👥</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          Групп пока нет
        </h3>
        <p className="text-gray-500">
          Добавьте первую группу, чтобы начать работу
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {groups.map((group) => (
        <div key={group.id} className="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-900">{group.name}</h3>
              <p className="text-sm text-gray-500">Курс {group.course || '-'}</p>
            </div>
            <div className="text-3xl">👥</div>
          </div>

          <div className="space-y-2 text-sm mb-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Студентов:</span>
              <span className="font-medium">{group.student_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Предметов:</span>
              <span className="font-medium">{group.subjects?.length || 0}</span>
            </div>
            {group.subjects && group.subjects.length > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Часов в неделю:</span>
                <span className="font-medium">
                  {group.subjects.reduce((sum, s) => sum + s.hours_per_week, 0)}
                </span>
              </div>
            )}
          </div>

          {group.subjects && group.subjects.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Предметы:</p>
              <div className="flex flex-wrap gap-1">
                {group.subjects.slice(0, 3).map((subj, idx) => (
                  <span
                    key={idx}
                    className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                  >
                    {subj.subject_name}
                  </span>
                ))}
                {group.subjects.length > 3 && (
                  <span className="inline-block bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                    +{group.subjects.length - 3}
                  </span>
                )}
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-2 pt-4 border-t">
            <button
              onClick={() => onEdit(group)}
              className="text-blue-600 hover:text-blue-900 text-sm"
            >
              Изменить
            </button>
            <button
              onClick={() => onDelete(group.id)}
              className="text-red-600 hover:text-red-900 text-sm"
            >
              Удалить
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}