import axios from 'axios';

// Используем относительный URL, чтобы работал прокси в Vite
const API_URL = '/api';

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
  
  // Этот метод теперь будет для старого алгоритма
  generate: (data) => api.post('/schedules/generate', data).then(res => res.data),
  
  export: async (id, type) => {
    const response = await api.get(`/schedules/${id}/export?type=${type}`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `schedule_${id}_${type}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  getConflicts: (id) => api.get(`/schedules/${id}/conflicts`).then(res => res.data),

  activate: (id) => api.post(`/schedules/${id}/activate`).then(res => res.data),
  
  delete: (id) => api.delete(`/schedules/${id}`).then(res => res.data),
};

export default api;