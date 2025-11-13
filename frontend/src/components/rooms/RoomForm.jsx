import { useState, useEffect } from 'react';

export default function RoomForm({ room, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    capacity: 30,
    building: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (room) {
      setFormData({
        name: room.name,
        capacity: room.capacity,
        building: room.building || ''
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
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4">
        {room ? 'Редактировать аудиторию' : 'Новая аудитория'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Номер/название <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="101"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Вместимость <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            min="1"
            max="500"
            value={formData.capacity}
            onChange={(e) => setFormData({ 
              ...formData, 
              capacity: parseInt(e.target.value) 
            })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Корпус</label>
          <input
            type="text"
            value={formData.building}
            onChange={(e) => setFormData({ ...formData, building: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="A"
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border rounded-lg hover:bg-gray-50"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </form>
    </div>
  );
}
