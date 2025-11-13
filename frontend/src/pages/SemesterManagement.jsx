import { useState, useEffect } from 'react';
import { academicYearService, semesterService } from '../services/semesterApi';

export default function SemesterManagement() {
  const [academicYears, setAcademicYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [semesters, setSemesters] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadData();
  }, []);
  
  useEffect(() => {
    if (selectedYear) {
      loadSemesters(selectedYear.id);
    }
  }, [selectedYear]);
  
  const loadData = async () => {
    try {
      setLoading(true);
      const years = await academicYearService.getAll();
      setAcademicYears(years);
      
      // Выбираем текущий год по умолчанию
      const currentYear = years.find(y => y.is_current) || years[0];
      setSelectedYear(currentYear);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      alert('Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  };
  
  const loadSemesters = async (yearId) => {
    try {
      const data = await semesterService.getAll(yearId);
      setSemesters(data);
    } catch (error) {
      console.error('Ошибка загрузки семестров:', error);
    }
  };
  
  const handleSetCurrent = async (yearId) => {
    try {
      await academicYearService.setCurrent(yearId);
      loadData();
    } catch (error) {
      alert('Ошибка при установке текущего года');
    }
  };
  
  const handleRegenerateWeeks = async (semesterId) => {
    if (!window.confirm('Пересоздать недели? Это удалит существующие занятия!')) return;
    
    try {
      const result = await semesterService.regenerateWeeks(semesterId);
      alert(`Создано ${result.weeks_count} недель`);
      loadSemesters(selectedYear.id);
    } catch (error) {
      alert('Ошибка при генерации недель');
    }
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
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Управление семестрами</h1>
        <p className="text-gray-600 mt-1">Учебные годы и семестры</p>
      </div>
      
      {/* Учебные годы */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Учебные годы</h2>
        </div>
        <div className="p-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {academicYears.map(year => (
              <div
                key={year.id}
                className={`p-4 rounded-lg border-2 cursor-pointer transition ${
                  selectedYear?.id === year.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedYear(year)}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold">{year.name}</h3>
                  {year.is_current && (
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                      Текущий
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">
                  {year.start_date} — {year.end_date}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Семестров: {year.semesters_count}
                </p>
                {!year.is_current && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSetCurrent(year.id);
                    }}
                    className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                  >
                    Сделать текущим
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Семестры выбранного года */}
      {selectedYear && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold">
              Семестры {selectedYear.name}
            </h2>
          </div>
          <div className="p-6">
            {semesters.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>Семестры не созданы</p>
                <p className="text-sm mt-2">
                  Запустите: <code className="bg-gray-100 px-2 py-1 rounded">python semester_data.py</code>
                </p>
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2">
                {semesters.map(semester => (
                  <SemesterCard
                    key={semester.id}
                    semester={semester}
                    onRegenerateWeeks={handleRegenerateWeeks}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Компонент карточки семестра
function SemesterCard({ semester, onRegenerateWeeks }) {
  const [weeks, setWeeks] = useState([]);
  const [showWeeks, setShowWeeks] = useState(false);
  
  const loadWeeks = async () => {
    try {
      const data = await semesterService.getWeeks(semester.id);
      setWeeks(data);
      setShowWeeks(true);
    } catch (error) {
      console.error('Ошибка загрузки недель:', error);
    }
  };
  
  const semesterTypeNames = {
    fall: '🍂 Осенний',
    spring: '🌸 Весенний'
  };
  
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-3 text-white">
        <h3 className="text-lg font-semibold">
          {semesterTypeNames[semester.type] || semester.type}
        </h3>
        <p className="text-sm text-blue-100">
          {semester.start_date} — {semester.end_date}
        </p>
      </div>
      
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-2xl font-bold text-gray-900">{semester.total_weeks}</p>
            <p className="text-sm text-gray-500">недель</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={loadWeeks}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
            >
              {showWeeks ? 'Скрыть' : 'Показать'} недели
            </button>
            <button
              onClick={() => onRegenerateWeeks(semester.id)}
              className="px-3 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 text-sm"
            >
              🔄 Пересоздать
            </button>
          </div>
        </div>
        
        {showWeeks && (
          <div className="mt-3 border-t pt-3">
            <div className="max-h-60 overflow-y-auto">
              <div className="grid grid-cols-2 gap-2">
                {weeks.map(week => (
                  <div
                    key={week.id}
                    className="text-xs p-2 bg-gray-50 rounded border border-gray-200"
                  >
                    <span className="font-semibold">Неделя {week.week_number}</span>
                    <div className="text-gray-600 mt-1">
                      {week.start_date} — {week.end_date}
                    </div>
                    {week.is_session && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
                        Сессия
                      </span>
                    )}
                    {week.is_vacation && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">
                        Каникулы
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}