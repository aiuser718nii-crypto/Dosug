export default function RoomList({ rooms, loading, onEdit, onDelete }) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <div className="spinner mx-auto"></div>
        <p className="text-gray-500 mt-2">Загрузка...</p>
      </div>
    );
  }

  if (rooms.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        Аудиторий пока нет
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {rooms.map((room) => (
        <div key={room.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-bold">{room.name}</h3>
              {room.building && (
                <p className="text-sm text-gray-500">Корпус {room.building}</p>
              )}
            </div>
            <div className="text-2xl">🏫</div>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Вместимость:</span>
              <span className="font-medium">{room.capacity} чел.</span>
            </div>
          </div>

          <div className="flex justify-end space-x-2 mt-4 pt-4 border-t">
            <button
              onClick={() => onEdit(room)}
              className="text-blue-600 hover:text-blue-900 text-sm"
            >
              Изменить
            </button>
            <button
              onClick={() => onDelete(room.id)}
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