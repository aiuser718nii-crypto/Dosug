export default function RoomList({ rooms, loading, onEdit, onDelete }) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="spinner mx-auto"></div>
        <p className="text-gray-500 mt-2">Загрузка аудиторий...</p>
      </div>
    );
  }

  if (rooms.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <div className="text-6xl mb-4">🏫</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          Аудиторий пока нет
        </h3>
        <p className="text-gray-500">
          Добавьте первую аудиторию, чтобы начать работу с расписанием.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {rooms.map((room) => (
        <div key={room.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 border-t-4 border-transparent hover:border-blue-500">
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                  <span>{room.name}</span>
                  {/* === ИНДИКАТОР СПЕЦИАЛЬНОЙ АУДИТОРИИ === */}
                  {room.is_special && (
                      <span 
                        className="text-xs font-bold text-purple-700 bg-purple-100 px-2.5 py-1 rounded-full" 
                        title="Специальная аудитория (лаборатория)"
                      >
                        LAB
                      </span>
                  )}
                </h3>
                {room.building && <p className="text-sm text-gray-500 mt-1">Корпус {room.building}</p>}
              </div>
              <div className="text-3xl opacity-70">🏫</div>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Вместимость:</span>
                <span className="font-semibold text-gray-900">{room.capacity} чел.</span>
              </div>
              {room.room_type && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Тип:</span>
                  <span className="font-semibold text-gray-900">{room.room_type}</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-4 p-4 bg-gray-50/70 border-t">
            <button
              onClick={() => onEdit(room)}
              className="text-blue-600 hover:text-blue-900 text-sm font-medium"
            >
              Изменить
            </button>
            <button
              onClick={() => onDelete(room.id)}
              className="text-red-600 hover:text-red-900 text-sm font-medium"
            >
              Удалить
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}