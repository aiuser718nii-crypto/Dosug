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
  
  const [formData, setFormData] = useState({
    name: '',
    population_size: 100,
    generations: 500,
    mutation_rate: 0.1
  });
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      setLoading(true);
      const [yearsData, semestersData] = await Promise.all([
        academicYearService.getAll(),
        semesterService.getAll()
      ]);
      
      setAcademicYears(yearsData);
      setSemesters(semestersData);
      
      // Выбираем первый семестр по умолчанию
      if (semestersData.length > 0) {
        setSelectedSemester(semestersData[0]);
        setFormData(prev => ({
          ...prev,
          name: `Расписание ${semestersData[0].type}`
        }));
      }
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      alert('Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  };
  
  const handleGenerate = async () => {
    if (!selectedSemester) {
      alert('Выберите семестр');
      return;
    }
    
    if (!window.confirm('Начать генерацию расписания? Это может занять несколько минут.')) {
      return;
    }
    
    try {
      setGenerating(true);
      setProgress({ stage: 'init', message: 'Инициализация...' });
      
      const year = academicYears.find(y => 
        y.id === semesters.find(s => s.id === selectedSemester.id)?.academic_year_id
      );
      
      const data = {
        semester_id: selectedSemester.id,
        name: formData.name,
        semester_label: selectedSemester.type,
        academic_year: year?.name || '2024/2025',
        population_size: formData.population_size,
        generations: formData.generations,
        mutation_rate: formData.mutation_rate
      };
      
      setProgress({ stage: 'generating', message: 'Генерация расписания...' });
      
      const result = await semesterScheduleService.generate(data);
      
      setProgress({ 
        stage: 'complete', 
        message: 'Готово!',
        result 
      });
      
      // Переход к просмотру через 2 секунды
      setTimeout(() => {
        navigate(`/schedules/${result.schedule_id}`);
      }, 2000);
      
    } catch (error) {
      console.error('Ошибка генерации:', error);
      alert(`Ошибка: ${error.response?.data?.error || error.message}`);
      setProgress(null);
    } finally {
      setGenerating(false);
    }
  };
  
  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="spinner mx-auto"></div>
          <p className="text-gray-500 mt-2">Загрузка...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Генерация семестрового расписания
        </h1>
        <p className="text-gray-600 mt-1">
          Автоматическое создание расписания на весь семестр
        </p>
      </div>
      
      {/* Выбор семестра */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">1. Выберите семестр</h2>
        
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
                    name: `Расписание ${semester.type} ${year?.name || ''}`
                  }));
                }}
                className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg">
                    {semester.type === 'fall' ? '🍂 Осенний' : '🌸 Весенний'}
                  </h3>
                  {isSelected && (
                    <span className="px-2 py-1 bg-blue-500 text-white text-xs rounded">
                      Выбран
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">
                  {year?.name || 'Учебный год не указан'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {semester.start_date} — {semester.end_date}
                </p>
                <p className="text-sm font-semibold text-blue-600 mt-2">
                  {semester.total_weeks} недель
                </p>
              </div>
            );
          })}
        </div>
        
        {semesters.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>Семестры не созданы</p>
            <p className="text-sm mt-2">
              Запустите: <code className="bg-gray-100 px-2 py-1 rounded">python semester_data.py</code>
            </p>
          </div>
        )}
      </div>
      
      {/* Настройки */}
      {selectedSemester && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">2. Настройки генерации</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Название расписания
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Например: Расписание осеннего семестра 2024"
              />
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Размер популяции
                  <span className="text-gray-400 text-xs ml-1">👥</span>
                </label>
                <input
                  type="number"
                  value={formData.population_size}
                  onChange={(e) => setFormData({ ...formData, population_size: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="20"
                  max="500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Больше = лучше качество, медленнее
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Поколений
                  <span className="text-gray-400 text-xs ml-1">🔄</span>
                </label>
                <input
                  type="number"
                  value={formData.generations}
                  onChange={(e) => setFormData({ ...formData, generations: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="100"
                  max="2000"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Рекомендуется: 500-1000
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Мутация
                  <span className="text-gray-400 text-xs ml-1">🧬</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.mutation_rate}
                  onChange={(e) => setFormData({ ...formData, mutation_rate: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="0.01"
                  max="0.5"
                />
                <p className="text-xs text-gray-500 mt-1">
                  0.1 = 10% вероятность
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Кнопка генерации */}
      {selectedSemester && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">3. Запуск генерации</h2>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-yellow-900 mb-2">⚠️ Внимание</h3>
            <ul className="text-sm text-yellow-800 space-y-1 list-disc list-inside">
              <li>Генерация может занять от 1 до 10 минут</li>
              <li>Убедитесь, что в базе данных есть все необходимые данные</li>
              <li>Проверьте, что у групп есть предметы</li>
              <li>Проверьте, что у преподавателей привязаны предметы</li>
            </ul>
          </div>
          
          <button
            onClick={handleGenerate}
            disabled={generating}
            className={`w-full py-3 rounded-lg font-semibold text-white transition ${
              generating
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {generating ? '⏳ Генерация...' : '🚀 Сгенерировать расписание'}
          </button>
        </div>
      )}
      
      {/* Прогресс */}
      {progress && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="text-center">
              {progress.stage === 'complete' ? (
                <>
                  <div className="text-6xl mb-4">✅</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    Расписание создано!
                  </h3>
                  <div className="space-y-2 text-sm text-gray-600">
                    <p>Занятий: {progress.result.lessons_count}</p>
                    <p>Качество: {(progress.result.fitness * 100).toFixed(1)}%</p>
                    <p>Конфликтов: {progress.result.conflicts_count}</p>
                  </div>
                  <p className="text-sm text-gray-500 mt-4">
                    Переход к просмотру...
                  </p>
                </>
              ) : (
                <>
                  <div className="spinner mx-auto mb-4"></div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {progress.message}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Пожалуйста, подождите...
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}