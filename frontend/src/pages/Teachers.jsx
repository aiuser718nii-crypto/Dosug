import { useState, useEffect } from 'react';
import { teacherService } from '../services/api'; 
import TeacherList from '../components/teachers/TeacherList';
import TeacherForm from '../components/teachers/TeacherForm';
import toast from 'react-hot-toast';



export default function Teachers() {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);

  useEffect(() => {
    loadTeachers();
  }, []);

  const loadTeachers = async () => {
    try {
      setLoading(true);
      const data = await teacherService.getAll();
      setTeachers(data);
    } catch (error) {
      toast.error('Ошибка загрузки преподавателей');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data) => {
    try {
      await teacherService.create(data);
      toast.success('Преподаватель добавлен');
      loadTeachers();
      setShowForm(false);
    } catch (error) {
      toast.error('Ошибка при добавлении');
    }
  };

  const handleEdit = (teacher) => {
    setEditingTeacher(teacher);
    setShowForm(true);
  };

  const handleUpdate = async (id, data) => {
    try {
      await teacherService.update(id, data);
      toast.success('Преподаватель обновлен');
      loadTeachers();
      setShowForm(false);
      setEditingTeacher(null);
    } catch (error) {
      toast.error('Ошибка при обновлении');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Удалить преподавателя?')) return;
    
    try {
      await teacherService.delete(id);
      toast.success('Преподаватель удален');
      loadTeachers();
    } catch (error) {
      toast.error('Ошибка при удалении');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Преподаватели</h1>
        <button
          onClick={() => {
            setEditingTeacher(null);
            setShowForm(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Добавить преподавателя
        </button>
      </div>

      {showForm && (
        <TeacherForm
          teacher={editingTeacher}
          onSubmit={editingTeacher 
            ? (data) => handleUpdate(editingTeacher.id, data)
            : handleCreate
          }
          onCancel={() => {
            setShowForm(false);
            setEditingTeacher(null);
          }}
        />
      )}

      <TeacherList
        teachers={teachers}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}