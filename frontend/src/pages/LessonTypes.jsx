import { useState, useEffect } from 'react';
import { lessonTypeService } from '../services/semesterApi';

export default function LessonTypes() {
  const [lessonTypes, setLessonTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingType, setEditingType] = useState(null);
  
  useEffect(() => {
    loadLessonTypes();
  }, []);
  
  const loadLessonTypes = async () => {
    try {
      setLoading(true);
      const data = await lessonTypeService.getAll();
      setLessonTypes(data);
    } catch (error) {
      console.error('Ошибка загрузки типов занятий:', error);
      alert('Не удалось загрузить типы занятий');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async (id) => {
    if (!window.confirm('Удалить этот тип занятия?')) return;
    
    try {
      await lessonTypeService.delete(id);
      loadLessonTypes();
    } catch (error) {
      alert('Ошибка при удалении');
    }
  };
  
  const handleEdit = (type) => {
    setEditingType(type);
    setShowForm(true);
  };
  
  const handleFormClose = () => {
    setShowForm(false);
    setEditingType(null);
    loadLessonTypes();
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
          <h1 className="text-3xl font-bold text-gray-900">Типы занятий</h1>
          <p className="text-gray-600 mt-1">Лекции, семинары, лабораторные и др.</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Добавить тип
        </button>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {lessonTypes.map(type => (
          <div
            key={type.id}
            className="bg-white rounded-lg shadow-md overflow-hidden border-l-4"
            style={{ borderLeftColor: type.color }}
          >
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-semibold text-gray-900">{type.name}</h3>
                <div
                  className="w-6 h-6 rounded"
                  style={{ backgroundColor: type.color }}
                ></div>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">⏱️</span>
                  <span>{type.duration_hours} часа(ов)</span>
                </div>
                
                {type.requires_special_room && (
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">🏫</span>
                    <span>Требует спец. аудиторию</span>
                  </div>
                )}
                
                {type.can_be_online && (
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">💻</span>
                    <span>Может быть онлайн</span>
                  </div>
                )}
              </div>
              
              <div className="mt-4 pt-4 border-t flex gap-2">
                <button
                  onClick={() => handleEdit(type)}
                  className="flex-1 px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 text-sm"
                >
                  Изменить
                </button>
                <button
                  onClick={() => handleDelete(type.id)}
                  className="flex-1 px-3 py-1 bg-red-50 text-red-600 rounded hover:bg-red-100 text-sm"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {lessonTypes.length === 0 && (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          <p>Типы занятий не созданы</p>
          <p className="text-sm mt-2">
            Запустите: <code className="bg-gray-100 px-2 py-1 rounded">python semester_data.py</code>
          </p>
        </div>
      )}
      
      {/* Модальное окно формы */}
      {showForm && (
        <LessonTypeFormModal
          lessonType={editingType}
          onClose={handleFormClose}
        />
      )}
    </div>
  );
}

// Модальное окно формы
function LessonTypeFormModal({ lessonType, onClose }) {
  const [formData, setFormData] = useState({
    code: lessonType?.code || 'lecture',
    name: lessonType?.name || '',
    description: lessonType?.description || '',
    duration_hours: lessonType?.duration_hours || 2,
    requires_special_room: lessonType?.requires_special_room || false,
    can_be_online: lessonType?.can_be_online || false,
    color: lessonType?.color || '#3B82F6'
  });
  
  const lessonTypeCodes = [
    { value: 'lecture', label: 'Лекция' },
    { value: 'seminar', label: 'Семинар' },
    { value: 'lab', label: 'Лабораторная работа' },
    { value: 'practice', label: 'Практическое занятие' },
    { value: 'field_trip', label: 'Выезд в поле' },
    { value: 'training_center', label: 'Выезд в учебный центр' },
    { value: 'production_visit', label: 'Выезд на производство' },
    { value: 'exercises', label: 'Выезд на учения' },
    { value: 'individual', label: 'Индивидуальное собеседование' },
    { value: 'exam', label: 'Экзамен' },
    { value: 'test', label: 'Зачёт' },
  ];
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (lessonType) {
        await lessonTypeService.update(lessonType.id, formData);
      } else {
        await lessonTypeService.create(formData);
      }
      onClose();
    } catch (error) {
      console.error('Ошибка сохранения:', error);
      alert('Ошибка при сохранении');
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold">
            {lessonType ? 'Редактировать' : 'Добавить'} тип занятия
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {!lessonType && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Тип
              </label>
              <select
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                required
              >
                {lessonTypeCodes.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Название
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Описание
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              rows="3"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Часов
              </label>
              <input
                type="number"
                value={formData.duration_hours}
                onChange={(e) => setFormData({ ...formData, duration_hours: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="1"
                max="24"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Цвет
              </label>
              <input
                type="color"
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-full h-10 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.requires_special_room}
                onChange={(e) => setFormData({ ...formData, requires_special_room: e.target.checked })}
                className="rounded"
              />
              <span className="text-sm text-gray-700">Требует специальную аудиторию</span>
            </label>
            
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.can_be_online}
                onChange={(e) => setFormData({ ...formData, can_be_online: e.target.checked })}
                className="rounded"
              />
              <span className="text-sm text-gray-700">Может проводиться онлайн</span>
            </label>
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