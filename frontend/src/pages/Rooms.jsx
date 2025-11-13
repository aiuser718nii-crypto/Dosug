import { useState, useEffect } from 'react';
import { roomService } from '../services/api';
import RoomList from '../components/rooms/RoomList';
import RoomForm from '../components/rooms/RoomForm';
import toast from 'react-hot-toast';

export default function Rooms() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState(null);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      setLoading(true);
      const data = await roomService.getAll();
      setRooms(data);
    } catch (error) {
      toast.error('Ошибка загрузки аудиторий');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data) => {
    try {
      await roomService.create(data);
      toast.success('Аудитория добавлена');
      loadRooms();
      setShowForm(false);
    } catch (error) {
      toast.error('Ошибка при добавлении');
    }
  };

  const handleEdit = (room) => {
    setEditingRoom(room);
    setShowForm(true);
  };

  const handleUpdate = async (id, data) => {
    try {
      await roomService.update(id, data);
      toast.success('Аудитория обновлена');
      loadRooms();
      setShowForm(false);
      setEditingRoom(null);
    } catch (error) {
      toast.error('Ошибка при обновлении');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Удалить аудиторию?')) return;
    
    try {
      await roomService.delete(id);
      toast.success('Аудитория удалена');
      loadRooms();
    } catch (error) {
      toast.error('Ошибка при удалении');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Аудитории</h1>
        <button
          onClick={() => {
            setEditingRoom(null);
            setShowForm(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Добавить аудиторию
        </button>
      </div>

      {showForm && (
        <RoomForm
          room={editingRoom}
          onSubmit={editingRoom 
            ? (data) => handleUpdate(editingRoom.id, data)
            : handleCreate
          }
          onCancel={() => {
            setShowForm(false);
            setEditingRoom(null);
          }}
        />
      )}

      <RoomList
        rooms={rooms}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}