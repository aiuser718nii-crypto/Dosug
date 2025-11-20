import { useState, useEffect } from 'react';

export default function RoomForm({ room, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    capacity: 30,
    building: '',
    is_special: false // Начальное состояние для нового поля
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (room) {
      setFormData({
        name: room.name || '',
        capacity: room.capacity || 30,
        building: room.building || '',
        is_special: room.is_special || false // Заполняем при редактировании
      });
    }
  }, [room]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 my-6 border border-gray-200">
      <h3 className="text-xl font-bold mb-6 text-gray-800">
        {room ? 'Редактировать аудиторию' : 'Новая аудитория'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Номер/название <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Например: 101 или Лаб-1"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Вместимость <span className="text-red-500">*</span>
                </label>
                <input
                    type="number"
                    min="1"
                    value={formData.capacity}
                    onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Корпус</label>
                <input
                    type="text"
                    value={formData.building}
                    onChange={(e) => setFormData({ ...formData, building: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Например: Главный"
                />
            </div>
        </div>

        {/* === НОВЫЙ БЛОК С CHECKBOX === */}
        <div className="pt-2">
            <label className="flex items-center space-x-3 cursor-pointer p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100">
                <input
                    type="checkbox"
                    checked={formData.is_special}
                    onChange={(e) => setFormData({ ...formData, is_special: e.target.checked })}
                    className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <div className="flex flex-col">
                    <span className="text-sm font-medium text-gray-800">Специальная аудитория</span>
                    <span className="text-xs text-gray-500 mt-1">
                        Отметьте, если это лаборатория или аудитория с уникальным оборудованием.
                    </span>
                </div>
            </label>
        </div>
        {/* ============================== */}

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Сохранение...' : (room ? 'Сохранить изменения' : 'Создать аудиторию')}
          </button>
        </div>
      </form>
    </div>
  );
}