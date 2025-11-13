import { useState, useEffect } from 'react';
import { constraintService, lessonTypeService } from '../services/semesterApi';


export default function Constraints() {
  const [constraints, setConstraints] = useState([]);
  const [lessonTypes, setLessonTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingConstraint, setEditingConstraint] = useState(null);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      setLoading(true);
      const [constraintsData, typesData] = await Promise.all([
        constraintService.getAll(),
        lessonTypeService.getAll()
      ]);
      setConstraints(constraintsData);
      setLessonTypes(typesData);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      alert('Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id) => {
    if (!window.confirm('Удалить это ограничение?')) return;
    
    try {
      await constraintService.delete(id);
      loadData();
    } catch (error) {
      alert('Ошибка при удалении');
    }
  };
  
  const handleEdit = (constraint) => {
    setEditingConstraint(constraint);
    setShowForm(true);
  };
  
  const handleFormClose = () => {
    setShowForm(false);
    setEditingConstraint(null);
    loadData();
  };
  
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="spinner mx-auto"></div>
          <p className="text-gray-500 mt-2">Загрузка...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Временные ограничения</h1>
          <p className="text-gray-600 mt-1">
            Правила распределения занятий во времени
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Добавить ограничение
        </button>
      </div>
      
      {/* Информационная панель */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">💡 Что это?</h3>
        <p className="text-sm text-blue-800">
          Ограничения определяют минимальное и максимальное количество дней между 
          разными типами занятий одного предмета. Например: между лекцией и семинаром 
          должно пройти минимум 3 дня.
        </p>
      </div>
      
      {/* Список ограничений */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                От типа
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                →
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                К типу
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Минимум дней
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Максимум дней
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {constraints.map((constraint) => (
              <tr key={constraint.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {constraint.type_from}
                  </span>
                </td>
                <td className="px-6 py-4 text-center text-gray-400">
                  →
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    {constraint.type_to}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-semibold text-gray-900">
                    {constraint.min_days_between}
                  </span>
                  <span className="text-gray-500 text-sm ml-1">дней</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {constraint.max_days_between ? (
                    <>
                      <span className="font-semibold text-gray-900">
                        {constraint.max_days_between}
                      </span>
                      <span className="text-gray-500 text-sm ml-1">дней</span>
                    </>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(constraint)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    Изменить
                  </button>
                  <button
                    onClick={() => handleDelete(constraint.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {constraints.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p>Ограничения не заданы</p>
            <p className="text-sm mt-2">
              Нажмите "Добавить ограничение" для создания правил
            </p>
          </div>
        )}
      </div>
      
      {/* Модальное окно формы */}
      {showForm && (
        <ConstraintFormModal
          constraint={editingConstraint}
          lessonTypes={lessonTypes}
          onClose={handleFormClose}
        />
      )}
    </div>
  );
}

// Модальное окно формы ограничения
function ConstraintFormModal({ constraint, lessonTypes, onClose }) {
  const [formData, setFormData] = useState({
    type_from_id: constraint?.type_from_id || lessonTypes[0]?.id || '',
    type_to_id: constraint?.type_to_id || lessonTypes[0]?.id || '',
    min_days_between: constraint?.min_days_between || 3,
    max_days_between: constraint?.max_days_between || 7,
    same_subject_only: constraint?.same_subject_only ?? true
  });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Валидация
    if (formData.type_from_id === formData.type_to_id) {
      alert('Типы занятий должны быть разными');
      return;
    }
    
    if (formData.max_days_between && formData.min_days_between > formData.max_days_between) {
      alert('Минимум дней не может быть больше максимума');
      return;
    }
    
    try {
      const data = {
        ...formData,
        type_from_id: parseInt(formData.type_from_id),
        type_to_id: parseInt(formData.type_to_id),
        max_days_between: formData.max_days_between || null
      };
      
      if (constraint) {
        await constraintService.update(constraint.id, data);
      } else {
        await constraintService.create(data);
      }
      onClose();
    } catch (error) {
      console.error('Ошибка сохранения:', error);
      alert('Ошибка при сохранении');
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold">
            {constraint ? 'Редактировать' : 'Добавить'} ограничение
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                От типа занятия
              </label>
              <select
                value={formData.type_from_id}
                onChange={(e) => setFormData({ ...formData, type_from_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                required
              >
                {lessonTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                К типу занятия
              </label>
              <select
                value={formData.type_to_id}
                onChange={(e) => setFormData({ ...formData, type_to_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                required
              >
                {lessonTypes.map(type => (
                  <option key={type.id} value={type.id}>{type.name}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="text-sm text-gray-700 mb-3">
              Между занятиями типа <strong>{lessonTypes.find(t => t.id === parseInt(formData.type_from_id))?.name}</strong> и <strong>{lessonTypes.find(t => t.id === parseInt(formData.type_to_id))?.name}</strong> должно пройти:
            </p>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Минимум дней
                </label>
                <input
                  type="number"
                  value={formData.min_days_between}
                  onChange={(e) => setFormData({ ...formData, min_days_between: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="0"
                  max="30"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Максимум дней
                  <span className="text-gray-400 text-xs ml-1">(необязательно)</span>
                </label>
                <input
                  type="number"
                  value={formData.max_days_between || ''}
                  onChange={(e) => setFormData({ ...formData, max_days_between: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="0"
                  max="30"
                  placeholder="Не ограничено"
                />
              </div>
            </div>
          </div>
          
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.same_subject_only}
                onChange={(e) => setFormData({ ...formData, same_subject_only: e.target.checked })}
                className="rounded"
              />
              <span className="text-sm text-gray-700">
                Только для одного предмета
              </span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">
              Если включено, ограничение применяется только к занятиям одного предмета
            </p>
          </div>
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Отмена
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}