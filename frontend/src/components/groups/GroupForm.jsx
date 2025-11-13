import { useState, useEffect } from 'react';

export default function GroupForm({ group, subjects, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    course: 1,
    student_count: 25,
    subjects: [] // [{subject_id, hours_per_week}]
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (group) {
      setFormData({
        name: group.name,
        course: group.course || 1,
        student_count: group.student_count,
        subjects: group.subjects?.map(s => ({
          subject_id: s.subject_id,
          hours_per_week: s.hours_per_week
        })) || []
      });
    }
  }, [group]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  const addSubject = () => {
    setFormData({
      ...formData,
      subjects: [...formData.subjects, { subject_id: '', hours_per_week: 2 }]
    });
  };

  const removeSubject = (index) => {
    setFormData({
      ...formData,
      subjects: formData.subjects.filter((_, i) => i !== index)
    });
  };

  const updateSubject = (index, field, value) => {
    const newSubjects = [...formData.subjects];
    newSubjects[index][field] = field === 'hours_per_week' ? parseInt(value) : value;
    setFormData({ ...formData, subjects: newSubjects });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4">
        {group ? 'Редактировать группу' : 'Новая группа'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Название <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Например: ПИ-101"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Курс</label>
            <select
              value={formData.course}
              onChange={(e) => setFormData({ ...formData, course: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1 курс</option>
              <option value={2}>2 курс</option>
              <option value={3}>3 курс</option>
              <option value={4}>4 курс</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Количество студентов <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            min="1"
            max="100"
            value={formData.student_count}
            onChange={(e) => setFormData({ ...formData, student_count: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* Предметы */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium">
              Предметы <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={addSubject}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              + Добавить предмет
            </button>
          </div>

          {formData.subjects.length === 0 ? (
            <div className="border-2 border-dashed rounded-lg p-4 text-center text-gray-500 text-sm">
              Нажмите "Добавить предмет" чтобы назначить предметы группе
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto border rounded-lg p-3">
              {formData.subjects.map((subj, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <select
                    value={subj.subject_id}
                    onChange={(e) => updateSubject(index, 'subject_id', parseInt(e.target.value))}
                    className="flex-1 px-3 py-2 border rounded-lg text-sm"
                    required
                  >
                    <option value="">Выберите предмет</option>
                    {subjects.map(s => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>

                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={subj.hours_per_week}
                    onChange={(e) => updateSubject(index, 'hours_per_week', e.target.value)}
                    className="w-20 px-3 py-2 border rounded-lg text-sm"
                    placeholder="Часов"
                    required
                  />
                  <span className="text-xs text-gray-500">ч/нед</span>

                  <button
                    type="button"
                    onClick={() => removeSubject(index)}
                    className="text-red-600 hover:text-red-800 p-2"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {subjects.length === 0 && (
          <p className="text-sm text-amber-600 bg-amber-50 p-3 rounded">
            ⚠️ Сначала создайте предметы, затем назначайте их группам
          </p>
        )}

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
            disabled={loading || formData.subjects.length === 0}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </form>
    </div>
  );
}