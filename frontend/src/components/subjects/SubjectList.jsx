export default function SubjectList({ subjects, loading, onEdit, onDelete }) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="spinner mx-auto"></div>
        <p className="text-gray-500 mt-2">Загрузка...</p>
      </div>
    );
  }

  if (subjects.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-6xl mb-4">📚</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          Предметов пока нет
        </h3>
        <p className="text-gray-500">
          Добавьте первый предмет, чтобы начать работу
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Название
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Код
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
              Действия
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {subjects.map((subject) => (
            <tr key={subject.id} className="hover:bg-gray-50">
              <td className="px-6 py-4">
                <div className="font-medium text-gray-900">{subject.name}</div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500">
                {subject.code || '-'}
              </td>
              <td className="px-6 py-4 text-right text-sm font-medium">
                <button
                  onClick={() => onEdit(subject)}
                  className="text-blue-600 hover:text-blue-900 mr-4"
                >
                  Изменить
                </button>
                <button
                  onClick={() => onDelete(subject.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  Удалить
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}