import { useState, useEffect } from 'react';
import { lessonTypeService } from '../../services/semesterApi';
import { subjectService } from '../../services/api';

export default function GroupForm({ group, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    name: '',
    course: 1,
    student_count: 25,
    subjects: [] // Структура: [{ subject_id, loads: [{ lesson_type_id, hours_per_week }] }]
  });

  const [allSubjects, setAllSubjects] = useState([]);
  const [allLessonTypes, setAllLessonTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);

  // Загрузка справочников при монтировании
  useEffect(() => {
    const loadData = async () => {
      try {
        setDataLoading(true);
        const [subjectsData, lessonTypesData] = await Promise.all([
          subjectService.getAll(),
          lessonTypeService.getAll()
        ]);
        setAllSubjects(subjectsData);
        setAllLessonTypes(lessonTypesData);
      } catch (error) {
        console.error("Ошибка загрузки справочников", error);
      } finally {
        setDataLoading(false);
      }
    };
    loadData();
  }, []);

  // Заполнение формы при редактировании группы
  useEffect(() => {
    if (group && allSubjects.length > 0 && allLessonTypes.length > 0) {
      setFormData({
        name: group.name || '',
        course: group.course || 1,
        student_count: group.student_count || 25,
        subjects: group.subjects?.map(s => ({
          subject_id: s.subject_id,
          loads: s.loads.map(l => ({
            lesson_type_id: l.lesson_type_id,
            hours_per_week: l.hours_per_week
          }))
        })) || []
      });
    }
  }, [group, allSubjects, allLessonTypes]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  // --- Функции для управления формой ---
  const addSubject = () => {
    setFormData(prev => ({
      ...prev,
      subjects: [
        ...prev.subjects,
        {
          subject_id: '',
          loads: [{ lesson_type_id: allLessonTypes[0]?.id || '', hours_per_week: 2 }]
        }
      ]
    }));
  };

  const removeSubject = (subjIndex) => {
    setFormData(prev => ({
      ...prev,
      subjects: prev.subjects.filter((_, i) => i !== subjIndex)
    }));
  };

  const updateSubjectId = (subjIndex, newId) => {
    const newSubjects = [...formData.subjects];
    newSubjects[subjIndex].subject_id = newId;
    setFormData({ ...formData, subjects: newSubjects });
  };

  const addLoad = (subjIndex) => {
    const newSubjects = [...formData.subjects];
    newSubjects[subjIndex].loads.push({ lesson_type_id: allLessonTypes[0]?.id || '', hours_per_week: 2 });
    setFormData({ ...formData, subjects: newSubjects });
  };

  const removeLoad = (subjIndex, loadIndex) => {
    const newSubjects = [...formData.subjects];
    newSubjects[subjIndex].loads = newSubjects[subjIndex].loads.filter((_, i) => i !== loadIndex);
    
    if (newSubjects[subjIndex].loads.length === 0) {
      removeSubject(subjIndex);
    } else {
      setFormData({ ...formData, subjects: newSubjects });
    }
  };

  const updateLoad = (subjIndex, loadIndex, field, value) => {
    const newSubjects = [...formData.subjects];
    const parsedValue = parseInt(value, 10);
    newSubjects[subjIndex].loads[loadIndex][field] = isNaN(parsedValue) ? '' : parsedValue;
    setFormData({ ...formData, subjects: newSubjects });
  };

  if (dataLoading) {
      return <div className="p-4 text-center">Загрузка справочников...</div>
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-bold mb-4">
        {group ? 'Редактировать группу' : 'Новая группа'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Название <span className="text-red-500">*</span></label>
            <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="w-full px-3 py-2 border rounded-lg" required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Курс</label>
            <select value={formData.course} onChange={(e) => setFormData({ ...formData, course: parseInt(e.target.value) })} className="w-full px-3 py-2 border rounded-lg">
              {[1,2,3,4,5,6].map(c => <option key={c} value={c}>{c} курс</option>)}
            </select>
          </div>
        </div>
        <div>
            <label className="block text-sm font-medium mb-1">Количество студентов <span className="text-red-500">*</span></label>
            <input type="number" min="1" value={formData.student_count} onChange={(e) => setFormData({ ...formData, student_count: parseInt(e.target.value) })} className="w-full px-3 py-2 border rounded-lg" required />
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium">Предметы и нагрузка <span className="text-red-500">*</span></label>
            <button type="button" onClick={addSubject} className="text-sm text-blue-600 hover:text-blue-800">+ Добавить предмет</button>
          </div>
          
          <div className="space-y-4">
            {formData.subjects.map((subj, subjIndex) => (
              <div key={subjIndex} className="border rounded-lg p-4 bg-gray-50/50">
                <div className="flex items-center gap-4 mb-3">
                  <select
                    value={subj.subject_id}
                    onChange={(e) => updateSubjectId(subjIndex, parseInt(e.target.value))}
                    className="flex-1 px-3 py-2 border rounded-lg font-semibold"
                    required
                  >
                    <option value="">-- Выберите предмет --</option>
                    {allSubjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                  <button type="button" onClick={() => removeSubject(subjIndex)} className="text-red-500 hover:text-red-700 p-2">✕</button>
                </div>

                <div className="space-y-2 pl-4">
                  {subj.loads.map((load, loadIndex) => (
                    <div key={loadIndex} className="flex items-center gap-2">
                      <select
                        value={load.lesson_type_id}
                        onChange={(e) => updateLoad(subjIndex, loadIndex, 'lesson_type_id', e.target.value)}
                        className="flex-1 px-2 py-1 border rounded-lg text-sm"
                        required
                      >
                        <option value="">-- Тип занятия --</option>
                        {allLessonTypes.map(lt => <option key={lt.id} value={lt.id}>{lt.name}</option>)}
                      </select>
                      <input
                        type="number" min="1"
                        value={load.hours_per_week}
                        onChange={(e) => updateLoad(subjIndex, loadIndex, 'hours_per_week', e.target.value)}
                        className="w-20 px-2 py-1 border rounded-lg text-sm"
                        required
                      />
                      <span className="text-xs text-gray-500">ч/нед</span>
                      <button type="button" onClick={() => removeLoad(subjIndex, loadIndex)} className="text-gray-400 hover:text-red-500 p-1">🗑️</button>
                    </div>
                  ))}
                  <button type="button" onClick={() => addLoad(subjIndex)} className="text-xs text-blue-500 hover:text-blue-700 mt-2">+ Добавить тип нагрузки</button>
                </div>
              </div>
            ))}
            {formData.subjects.length === 0 && (
              <div className="border-2 border-dashed rounded-lg p-6 text-center text-gray-500">
                Нажмите "+ Добавить предмет", чтобы определить учебную нагрузку
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button type="button" onClick={onCancel} className="px-4 py-2 border rounded-lg hover:bg-gray-50">Отмена</button>
          <button type="submit" disabled={loading || formData.subjects.length === 0} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {loading ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </form>
    </div>
  );
}