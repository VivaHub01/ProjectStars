import api from './axios';

export const register = async (email, password, role) => {
  try {
    const response = await api.post('/register', {
      email, 
      password,
      role 
    });
    return response.data;
  } catch (err) {
    console.error('Registration error:', err.response); // Добавьте логирование
    throw err;
  }
};

export const login = async (email, password) => {
  const response = await api.post('/login', 
    `username=${email}&password=${password}&grant_type=password`,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );
  return response.data;
};

export const verifyEmail = async (token) => {
  return api.get(`/verify-email?token=${token}`);
};

export const requestPasswordReset = async (email) => {
  return api.post('/request-password-reset', { email });
};

export const resetPassword = async (token, newPassword) => {
  return api.post('/reset-password', { token, new_password: newPassword });
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};