import { useState, useEffect } from 'react';
import { subjectService } from '../../services/api';

export default function TeacherForm({ teacher, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    max_hours_per_week: 20,
    subject_ids: []
  });
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSubjects();
    
    if (teacher) {
      setFormData({
        name: teacher.name,
        email: teacher.email || '',
        max_hours_per_week: teacher.max_hours_per_week,
        subject_ids: teacher.subjects?.map(s => s.id) || []
      });
    }
  }, [teacher]);

  const loadSubjects = async () => {
    try {
      const data = await subjectService.getAll();
      setSubjects(data);
    } catch (error) {
      console.error('Ошибка загрузки предметов:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  const toggleSubject = (subjectId) => {
    setFormData(prev => ({
      ...prev,
      subject_ids: prev.subject_ids.includes(subjectId)
        ? prev.subject_ids.filter(id => id !== subjectId)
        : [...prev.subject_ids, subjectId]
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4">
        {teacher ? 'Редактировать преподавателя' : 'Новый преподаватель'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            ФИО <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Максимум часов в неделю
          </label>
          <input
            type="number"
            min="1"
            max="40"
            value={formData.max_hours_per_week}
            onChange={(e) => setFormData({ 
              ...formData, 
              max_hours_per_week: parseInt(e.target.value) 
            })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Предметы <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto border rounded-lg p-3">
            {subjects.map(subject => (
              <label key={subject.id} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={formData.subject_ids.includes(subject.id)}
                  onChange={() => toggleSubject(subject.id)}
                  className="rounded text-blue-600"
                />
                <span className="text-sm">{subject.name}</span>
              </label>
            ))}
          </div>
          {subjects.length === 0 && (
            <p className="text-sm text-gray-500 mt-2">
              Сначала создайте предметы
            </p>
          )}
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
            disabled={loading || formData.subject_ids.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </form>
    </div>
  );
}