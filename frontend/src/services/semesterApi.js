import api from './api';

// ==================== Учебные годы ====================
export const academicYearService = {
  getAll: () => api.get('/academic-years').then(res => res.data),
  
  create: (data) => api.post('/academic-years', data).then(res => res.data),
  
  setCurrent: (id) => api.post(`/academic-years/${id}/set-current`).then(res => res.data),
};

// ==================== Семестры ====================
export const semesterService = {
  getAll: (academicYearId = null) => {
    const params = academicYearId ? { academic_year_id: academicYearId } : {};
    return api.get('/semesters', { params }).then(res => res.data);
  },
  
  getById: (id) => api.get(`/semesters/${id}`).then(res => res.data),
  
  create: (data) => api.post('/semesters', data).then(res => res.data),
  
  getWeeks: (semesterId) => api.get(`/semesters/${semesterId}/weeks`).then(res => res.data),
  
  regenerateWeeks: (semesterId) => 
    api.post(`/semesters/${semesterId}/regenerate-weeks`).then(res => res.data),
};

// ==================== Типы занятий ====================
export const lessonTypeService = {
  getAll: () => api.get('/lesson-types').then(res => res.data),
  
  getById: (id) => api.get(`/lesson-types/${id}`).then(res => res.data),
  
  create: (data) => api.post('/lesson-types', data).then(res => res.data),
  
  update: (id, data) => api.put(`/lesson-types/${id}`, data).then(res => res.data),
  
  delete: (id) => api.delete(`/lesson-types/${id}`).then(res => res.data),
};

// ==================== Ограничения ====================
export const constraintService = {
  getAll: () => api.get('/lesson-type-constraints').then(res => res.data),
  
  create: (data) => api.post('/lesson-type-constraints', data).then(res => res.data),
  
  update: (id, data) => api.put(`/lesson-type-constraints/${id}`, data).then(res => res.data),
  
  delete: (id) => api.delete(`/lesson-type-constraints/${id}`).then(res => res.data),
};

// ==================== Генерация расписания ====================
export const semesterScheduleService = {
  generate: (data) => api.post('/schedules/generate-semester', data).then(res => res.data),
  
  getExtended: (scheduleId) => 
    api.get(`/schedules/${scheduleId}/extended`).then(res => res.data),
  
  getWeek: (scheduleId, weekNumber) => 
    api.get(`/schedules/${scheduleId}/week/${weekNumber}`).then(res => res.data),
};

// ==================== Статистика ====================
export const statisticsService = {
  getSemesterStats: (semesterId) => 
    api.get(`/statistics/semester/${semesterId}`).then(res => res.data),
};

export default {
  academicYearService,
  semesterService,
  lessonTypeService,
  constraintService,
  semesterScheduleService,
  statisticsService,
};