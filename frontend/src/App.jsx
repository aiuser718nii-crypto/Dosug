import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import Layout from './components/common/SideBar';
import Home from './pages/Home';
import Teachers from './pages/Teachers';
import Rooms from './pages/Rooms';
import Subjects from './pages/Subjects';
import Groups from './pages/Groups';
import ScheduleView from './pages/ScheduleView';
import SemesterManagement from './pages/SemesterManagement';
import LessonTypes from './pages/LessonTypes';
import Constraints from './pages/Constraints';
import GenerateSemester from './pages/GenerateSemester';
import SemesterScheduleView from './pages/SemesterScheduleView';
import Schedules from './pages/Schedules';

import { scheduleService } from './services/api';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          
          {/* Справочники */}
          <Route path="teachers" element={<Teachers />} />
          <Route path="rooms" element={<Rooms />} />
          <Route path="subjects" element={<Subjects />} />
          <Route path="groups" element={<Groups />} />
          
          {/* Расписания */}
          <Route path="schedules" element={<Schedules />} />
          {/* ИСПРАВЛЕНИЕ: Используем умный компонент */}
          <Route path="schedules/:id" element={<SmartScheduleView />} />
          
          {/* Семестровая система */}
          <Route path="semesters" element={<SemesterManagement />} />
          <Route path="lesson-types" element={<LessonTypes />} />
          <Route path="constraints" element={<Constraints />} />
          
          {/* Генерация */}
          <Route path="generate-semester" element={<GenerateSemester />} />
          
          {/* 404 - Перенаправление на главную */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

// Компонент-переключатель для просмотра расписаний
function SmartScheduleView() {
  const { id } = useParams();
  const [scheduleType, setScheduleType] = useState(null); // 'simple' или 'semester'

  useEffect(() => {
    // Делаем запрос, чтобы определить тип расписания по его данным
    scheduleService.getById(id)
      .then(data => {
        // Условие: если у расписания есть метод генерации CSP или есть недели,
        // то это семестровое расписание.
        if (data.generation_method?.includes('csp') || (data.weeks && data.weeks.length > 0)) {
          setScheduleType('semester');
        } else {
          setScheduleType('simple');
        }
      })
      .catch(() => {
        setScheduleType('error'); // Если расписание не найдено
      });
  }, [id]);

  if (scheduleType === 'semester') {
    return <SemesterScheduleView />;
  }
  
  if (scheduleType === 'simple') {
    return <ScheduleView />;
  }
  
  if (scheduleType === 'error') {
    return (
        <div className="text-center p-8">
            <h2 className="text-xl font-bold text-red-600">Ошибка</h2>
            <p className="text-gray-500">Расписание с ID {id} не найдено.</p>
        </div>
    );
  }

  // Пока идет определение типа, показываем загрузчик
  return (
    <div className="flex justify-center items-center h-96">
      <div className="spinner"></div>
    </div>
  );
}

export default App;