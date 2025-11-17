import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  semesterService, 
  academicYearService,
  semesterScheduleService 
} from '../services/semesterApi';

export default function GenerateSemester() {
  const navigate = useNavigate();
  const [academicYears, setAcademicYears] = useState([]);
  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    max_iterations: 500000,
    max_lessons_per_day: 5,
    min_days_between_lessons: 2, 
  });
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [yearsData, semestersData] = await Promise.all([
        academicYearService.getAll(),
        semesterService.getAll()
      ]);
      
      setAcademicYears(yearsData);
      setSemesters(semestersData);
      
      if (semestersData.length > 0) {
        const lastSemester = semestersData.sort((a, b) => new Date(b.start_date) - new Date(a.start_date))[0];
        setSelectedSemester(lastSemester);
        const year = yearsData.find(y => y.id === lastSemester.academic_year_id);
        setFormData(prev => ({
          ...prev,
          name: `Расписание ${lastSemester.type === 'fall' ? 'осеннего' : 'весеннего'} семестра ${year?.name || ''}`
        }));
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      setError('Не удалось загрузить данные для генерации. Проверьте консоль.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleGenerate = async () => {
    if (!selectedSemester) {
      alert('Выберите семестр');
      return;
    }
    if (!formData.name.trim()) {
      alert('Введите название расписания');
      return;
    }
    if (!window.confirm('Начать генерацию расписания с помощью CSP алгоритма? Это может занять некоторое время.')) {
      return;
    }
    
    try {
      setGenerating(true);
      setError(null);
      setProgress({ stage: 'generating', message: 'CSP алгоритм ищет идеальное решение...' });
      
      const year = academicYears.find(y => y.id === selectedSemester.academic_year_id);
      
      const data = {
        semester_id: selectedSemester.id,
        name: formData.name,
        semester_label: selectedSemester.type === 'fall' ? 'Осенний семестр' : 'Весенний семестр',
        academic_year: year?.name || '2024/2025',
        max_iterations: formData.max_iterations,
        max_lessons_per_day: formData.max_lessons_per_day,
        min_days_between_lessons: formData.min_days_between_lessons,
      };
      
      const result = await semesterScheduleService.generate(data);
      
      if (result.schedule_id) {
        setProgress({ 
          stage: 'complete_success', 
          message: 'Готово!',
          result 
        });
        
        setTimeout(() => {
          navigate(`/schedules/${result.schedule_id}`);
        }, 2500);

      } else {
        setProgress({
          stage: 'complete_failure',
          message: 'Не удалось найти полное решение',
          result,
        });
      }
      
    } catch (error) {
      console.error('Ошибка генерации:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Произошла неизвестная ошибка.';
      setError(errorMessage);
      setProgress(null);
    } finally {
      setGenerating(false);
    }
  };

  const closeProgressModal = () => {
    setProgress(null);
  }
  
  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="spinner mx-auto"></div>
          <p className="text-gray-500 mt-2">Загрузка...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          🎯 Генерация семестрового расписания (CSP)
        </h1>
        <p className="text-gray-600 mt-1">
          Использует алгоритм Constraint Satisfaction Problem для создания идеального расписания без конфликтов.
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
          <p className="font-bold">Ошибка!</p>
          <p>{error}</p>
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <span className="text-2xl">1️⃣</span>
          <span>Выберите семестр</span>
        </h2>
        
        <div className="grid gap-4 md:grid-cols-2">
          {semesters.map(semester => {
            const year = academicYears.find(y => y.id === semester.academic_year_id);
            const isSelected = selectedSemester?.id === semester.id;
            
            return (
              <div
                key={semester.id}
                onClick={() => {
                  setSelectedSemester(semester);
                  setFormData(prev => ({
                    ...prev,
                    name: `Расписание ${semester.type === 'fall' ? 'осеннего' : 'весеннего'} семестра ${year?.name || ''}`
                  }));
                }}
                className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-blue-300 hover:shadow'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg">
                    {semester.type === 'fall' ? '🍂 Осенний семестр' : '🌸 Весенний семестр'}
                  </h3>
                  {isSelected && (
                    <span className="px-3 py-1 bg-blue-500 text-white text-xs rounded-full font-semibold">
                      ✓ Выбран
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 font-medium">
                  {year?.name || 'Учебный год не указан'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  📅 {semester.start_date} — {semester.end_date}
                </p>
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-sm font-semibold text-blue-600">
                    📊 {semester.total_weeks} учебных недель
                  </p>
                </div>
              </div>
            );
          })}
        </div>
        
        {semesters.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-3">📅</div>
            <p className="font-medium">Семестры не созданы</p>
            <p className="text-sm mt-2">
              Для создания данных по умолчанию запустите скрипт в терминале.
            </p>
          </div>
        )}
      </div>
      
      {selectedSemester && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">2️⃣</span>
            <span>Настройки CSP алгоритма</span>
          </h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                📝 Название расписания
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Например: Расписание осеннего семестра 2024/2025"
              />
            </div>
            
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span>⚙️</span>
                <span>Основные ограничения</span>
              </h3>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Максимум пар в день
                  </label>
                  <input
                    type="number"
                    value={formData.max_lessons_per_day}
                    onChange={(e) => setFormData({ ...formData, max_lessons_per_day: parseInt(e.target.value) || 4 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    min="1" max="7"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Жесткое ограничение на количество занятий в учебный день. Рекомендуется: 4-5.
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Перерыв между занятиями по 1 предмету (дней)
                  </label>
                  <input
                    type="number"
                    value={formData.min_days_between_lessons}
                    onChange={(e) => setFormData({ ...formData, min_days_between_lessons: parseInt(e.target.value) || 1 })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    min="1" max="5"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    Чтобы не было 2 лекций по матанализу подряд. 2 = 1 день перерыва. Рекомендуется: 2.
                  </p>
                </div>
              </div>
            </div>
            
            <div>
              <details className="group">
                <summary className="cursor-pointer font-semibold text-gray-700 hover:text-gray-900 flex items-center gap-2">
                  <span className="group-open:rotate-90 transition-transform">▶</span>
                  <span>Расширенные настройки</span>
                </summary>
                
                <div className="mt-4 space-y-4 pl-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      🔄 Максимум итераций
                    </label>
                    <input
                      type="number"
                      value={formData.max_iterations}
                      onChange={(e) => setFormData({ ...formData, max_iterations: parseInt(e.target.value) || 100000 })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      min="10000"
                      max="2000000"
                      step="50000"
                    />
                    <p className="text-xs text-gray-600 mt-1">
                      Ограничение на глубину поиска. Увеличьте, если не находит решение. Рекомендуется: 500,000+.
                    </p>
                  </div>
                </div>
              </details>
            </div>
          </div>
        </div>
      )}
      
      {selectedSemester && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span className="text-2xl">3️⃣</span>
            <span>Запуск генерации</span>
          </h2>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
              <span>⚠️</span>
              <span>Перед запуском убедитесь:</span>
            </h3>
            <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
              <li>У всех групп есть предметы с указанием часов в неделю.</li>
              <li>У всех преподавателей привязаны предметы, которые они ведут.</li>
              <li>В базе есть достаточное количество активных аудиторий.</li>
              <li>Для выбранного семестра созданы недели.</li>
            </ul>
          </div>
          
          <button
            onClick={handleGenerate}
            disabled={generating}
            className={`w-full py-4 rounded-lg font-bold text-lg text-white transition shadow-lg ${
              generating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 hover:shadow-xl'
            }`}
          >
            {generating ? (
              <span className="flex items-center justify-center gap-2">
                <div className="spinner-small"></div>
                Генерация идёт...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <span>🎯</span>
                <span>Сгенерировать расписание</span>
              </span>
            )}
          </button>
          
          {!generating && (
            <p className="text-center text-sm text-gray-500 mt-3">
              ⏱️ Обычное время генерации: от 3 до 20 секунд
            </p>
          )}
        </div>
      )}
      
      {progress && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-50 backdrop-blur-sm" onClick={closeProgressModal}>
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-8 animate-fade-in" onClick={e => e.stopPropagation()}>
            <div className="text-center">

              {progress.stage === 'generating' && (
                <>
                  <div className="spinner-large mx-auto mb-4"></div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {progress.message}
                  </h3>
                  <p className="text-gray-600">
                    Это может занять от нескольких секунд до минуты...
                  </p>
                </>
              )}

              {progress.stage === 'complete_success' && (
                <>
                  <div className="text-7xl mb-4 animate-bounce">✅</div>
                  <h3 className="text-2xl font-bold text-green-700 mb-4">
                    Расписание создано!
                  </h3>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2 text-left">
                    <div className="flex justify-between items-center"><span className="text-sm font-medium text-gray-700">Занятий:</span><span className="text-lg font-bold text-green-700">{progress.result.lessons_count}</span></div>
                    <div className="flex justify-between items-center"><span className="text-sm font-medium text-gray-700">Качество:</span><span className="text-lg font-bold text-green-700">{(progress.result.fitness * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between items-center"><span className="text-sm font-medium text-gray-700">Время:</span><span className="text-lg font-bold text-blue-700">{progress.result.time.toFixed(2)}с</span></div>
                  </div>
                  <p className="text-sm text-gray-500 mt-4 animate-pulse">
                    Перенаправляем на страницу просмотра...
                  </p>
                </>
              )}

              {progress.stage === 'complete_failure' && (
                <>
                  <div className="text-7xl mb-4">⚠️</div>
                  <h3 className="text-2xl font-bold text-yellow-700 mb-4">
                    Решение не найдено
                  </h3>
                  <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 space-y-2 text-left">
                    <div className="flex justify-between items-center"><span className="text-sm font-medium text-gray-700">Прогресс:</span><span className="text-lg font-bold text-yellow-800">{(progress.result.fitness * 100).toFixed(1)}%</span></div>
                    <div className="flex justify-between items-center"><span className="text-sm font-medium text-gray-700">Итераций:</span><span className="text-lg font-bold text-gray-800">{progress.result.iterations.toLocaleString()}</span></div>
                    {progress.result.conflicts && progress.result.conflicts.length > 0 && (
                      <p className="text-xs text-red-700 pt-2 border-t border-yellow-200">{progress.result.conflicts[0].message}</p>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-4">
                    Попробуйте увеличить "Максимум итераций" или ослабить ограничения (например, увеличить макс. пар в день).
                  </p>
                  <button onClick={closeProgressModal} className="mt-6 w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700">
                    Понятно
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}