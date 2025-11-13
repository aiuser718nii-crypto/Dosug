import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { scheduleService } from '../services/api';
import toast from 'react-hot-toast';

export default function Generate() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    semester: 'Осенний 2023',
    academic_year: '2023/2024',
    method: 'genetic',
    population_size: 100,
    generations: 500,
    mutation_rate: 0.01,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await scheduleService.generate(formData);
      
      toast.success('Расписание успешно сгенерировано!');
      
      if (result.conflicts && result.conflicts.length > 0) {
        toast.error(`Найдено конфликтов: ${result.conflicts.length}`);
      }
      
      navigate(`/schedules/${result.schedule.id}`);
    } catch (error) {
      toast.error('Ошибка при генерации расписания');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Генерация расписания</h1>
      
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Название расписания
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Семестр</label>
            <input
              type="text"
              value={formData.semester}
              onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Учебный год</label>
            <input
              type="text"
              value={formData.academic_year}
              onChange={(e) => setFormData({ ...formData, academic_year: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Метод генерации
          </label>
          <select
            value={formData.method}
            onChange={(e) => setFormData({ ...formData, method: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg"
          >
            <option value="genetic">Генетический алгоритм</option>
            <option value="csp">CSP (пока недоступно)</option>
            <option value="hybrid">Гибридный (пока недоступно)</option>
          </select>
        </div>

        {formData.method === 'genetic' && (
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium">Параметры генетического алгоритма</h3>
            
            <div>
              <label className="block text-sm mb-1">
                Размер популяции: {formData.population_size}
              </label>
              <input
                type="range"
                min="50"
                max="200"
                value={formData.population_size}
                onChange={(e) => setFormData({ ...formData, population_size: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm mb-1">
                Количество поколений: {formData.generations}
              </label>
              <input
                type="range"
                min="100"
                max="1000"
                step="50"
                value={formData.generations}
                onChange={(e) => setFormData({ ...formData, generations: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm mb-1">
                Вероятность мутации: {formData.mutation_rate}
              </label>
              <input
                type="range"
                min="0.001"
                max="0.1"
                step="0.001"
                value={formData.mutation_rate}
                onChange={(e) => setFormData({ ...formData, mutation_rate: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Генерация...' : 'Сгенерировать расписание'}
        </button>
      </form>
    </div>
  );
}