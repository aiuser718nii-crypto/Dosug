import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/SideBar';

// Существующие страницы
import Home from './pages/Home';
import Teachers from './pages/Teachers';
import Rooms from './pages/Rooms';
import Subjects from './pages/Subjects';
import Groups from './pages/Groups';
import ScheduleView from './pages/ScheduleView';

// Новые страницы
import SemesterManagement from './pages/SemesterManagement';
import LessonTypes from './pages/LessonTypes';
import Constraints from './pages/Constraints';
import GenerateSemester from './pages/GenerateSemester';
import SemesterScheduleView from './pages/SemesterScheduleView';
import Schedules from './pages/Schedules';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          
          {/* Базовые разделы */}
          <Route path="teachers" element={<Teachers />} />
          <Route path="rooms" element={<Rooms />} />
          <Route path="subjects" element={<Subjects />} />
          <Route path="groups" element={<Groups />} />
          
          {/* Расписания */}
          <Route path="schedules" element={<Schedules />} />
          <Route path="schedules/:id" element={<SemesterScheduleView />} />
          <Route path="schedules/:id" element={<ScheduleView />} />
          {/* Семестровая система */}
          <Route path="semesters" element={<SemesterManagement />} />
          <Route path="lesson-types" element={<LessonTypes />} />
          <Route path="constraints" element={<Constraints />} />
          <Route path="generate-semester" element={<GenerateSemester />} />
          
          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;