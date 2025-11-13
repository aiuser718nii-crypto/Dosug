import { useState, useEffect } from 'react';
import { subjectService } from '../services/api';
import SubjectList from '../components/subjects/SubjectList';
import SubjectForm from '../components/subjects/SubjectForm';
import toast from 'react-hot-toast';

export default function Subjects() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingSubject, setEditingSubject] = useState(null);

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      setLoading(true);
      const data = await subjectService.getAll();
      setSubjects(data);
    } catch (error) {
      toast.error('Ошибка загрузки предметов');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (data) => {
    try {
      await subjectService.create(data);
      toast.success('Предмет добавлен');
      loadSubjects();
      setShowForm(false);
    } catch (error) {
      toast.error('Ошибка при добавлении');
    }
  };

  const handleEdit = (subject) => {
    setEditingSubject(subject);
    setShowForm(true);
  };

  const handleUpdate = async (id, data) => {
    try {
      await subjectService.update(id, data);
      toast.success('Предмет обновлен');
      loadSubjects();
      setShowForm(false);
      setEditingSubject(null);
    } catch (error) {
      toast.error('Ошибка при обновлении');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Удалить предмет?')) return;
    
    try {
      await subjectService.delete(id);
      toast.success('Предмет удален');
      loadSubjects();
    } catch (error) {
      toast.error('Ошибка при удалении');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Предметы</h1>
          <p className="text-gray-500 mt-1">
            Управление учебными дисциплинами
          </p>
        </div>
        <button
          onClick={() => {
            setEditingSubject(null);
            setShowForm(true);
          }}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <span>+</span>
          <span>Добавить предмет</span>
        </button>
      </div>

      {showForm && (
        <SubjectForm
          subject={editingSubject}
          onSubmit={editingSubject 
            ? (data) => handleUpdate(editingSubject.id, data)
            : handleCreate
          }
          onCancel={() => {
            setShowForm(false);
            setEditingSubject(null);
          }}
        />
      )}

      <SubjectList
        subjects={subjects}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}