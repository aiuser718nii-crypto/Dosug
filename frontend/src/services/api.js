// frontend/src/services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Обработка ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ==================== TEACHERS ====================
export const teacherService = {
  getAll: () => api.get('/teachers').then(res => res.data),
  getById: (id) => api.get(`/teachers/${id}`).then(res => res.data),
  create: (data) => api.post('/teachers', data).then(res => res.data),
  update: (id, data) => api.put(`/teachers/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/teachers/${id}`).then(res => res.data),
};

// ==================== ROOMS ====================
export const roomService = {
  getAll: () => api.get('/rooms').then(res => res.data),
  getById: (id) => api.get(`/rooms/${id}`).then(res => res.data),
  create: (data) => api.post('/rooms', data).then(res => res.data),
  update: (id, data) => api.put(`/rooms/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/rooms/${id}`).then(res => res.data),
};

// ==================== SUBJECTS ====================
export const subjectService = {
  getAll: () => api.get('/subjects').then(res => res.data),
  getById: (id) => api.get(`/subjects/${id}`).then(res => res.data),
  create: (data) => api.post('/subjects', data).then(res => res.data),
  update: (id, data) => api.put(`/subjects/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/subjects/${id}`).then(res => res.data),
};

// ==================== GROUPS ====================
export const groupService = {
  getAll: () => api.get('/groups').then(res => res.data),
  getById: (id) => api.get(`/groups/${id}`).then(res => res.data),
  create: (data) => api.post('/groups', data).then(res => res.data),
  update: (id, data) => api.put(`/groups/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/groups/${id}`).then(res => res.data),
};

// ==================== SCHEDULES ====================
export const scheduleService = {
  getAll: () => api.get('/schedules').then(res => res.data),
  getById: (id) => api.get(`/schedules/${id}`).then(res => res.data),
  getExtended: (id) => api.get(`/schedules/${id}/extended`).then(res => res.data),
  getWeek: (id, weekNumber) => api.get(`/schedules/${id}/week/${weekNumber}`).then(res => res.data),
  generate: (data) => api.post('/schedules/generate-semester', data).then(res => res.data),
  
  export: async (id) => {
    try {
      const response = await api.get(`/schedules/${id}/export`, {
        responseType: 'blob',
      });
      
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `schedule-${id}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export error:', error);
      throw error;
    }
  },
  
  delete: (id) => api.delete(`/schedules/${id}`).then(res => res.data),
};

// ==================== STATS ====================
export const statsService = {
  getDashboard: () => api.get('/stats/dashboard').then(res => res.data),
};

// ==================== LESSON TYPES ====================
export const lessonTypeService = {
  getAll: () => api.get('/lesson-types').then(res => res.data),
  getById: (id) => api.get(`/lesson-types/${id}`).then(res => res.data),
  create: (data) => api.post('/lesson-types', data).then(res => res.data),
  update: (id, data) => api.put(`/lesson-types/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/lesson-types/${id}`).then(res => res.data),
};

// ==================== SEMESTERS ====================
export const semesterService = {
  getAll: () => api.get('/semesters').then(res => res.data),
  getById: (id) => api.get(`/semesters/${id}`).then(res => res.data),
  getWeeks: (id) => api.get(`/semesters/${id}/weeks`).then(res => res.data),
  create: (data) => api.post('/semesters', data).then(res => res.data),
  regenerateWeeks: (id) => api.post(`/semesters/${id}/regenerate-weeks`).then(res => res.data),
};

// ==================== ACADEMIC YEARS ====================
export const academicYearService = {
  getAll: () => api.get('/academic-years').then(res => res.data),
  create: (data) => api.post('/academic-years', data).then(res => res.data),
  setCurrent: (id) => api.post(`/academic-years/${id}/set-current`).then(res => res.data),
};

// Экспорт axios для прямого использования
export default api;