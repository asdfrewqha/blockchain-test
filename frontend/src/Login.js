import { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from './components/Logo';
import { validateLogin } from './components/validation';
import './styles/signup.css';
import Navbar from './components/NavBar';
import apiRequest from './components/Requests';

const LogInPage = () => {

  const [formData, setFormData] = useState({
    identifier: '',
    password: '',
    termsAccepted: false
  });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');


  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

const handleSubmit = async (e) => {
  e.preventDefault();

  const validationResult = validateLogin(formData);
  formData.username = formData.identifier;

  if (validationResult.isValid) {
    try {
      const response = await fetch('https://api.vote.vickz.ru/api/v2/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.msg || 'Login error');
      }

      const result = await response.json();
      console.log('Ответ от сервера:', result);

      // Сохраняем токены
      localStorage.setItem('access_token', result.access_token);
      localStorage.setItem('refresh_token', result.refresh_token);
      localStorage.setItem('private_key', result.private_key)

      // Запрашиваем профиль
      const profileResponse = await apiRequest({
        url: 'https://api.vote.vickz.ru/api/v2/profile',
        method: 'GET',
        auth: true
      });

      if (!profileResponse.ok) {
        throw new Error('Failed to fetch profile');
      }

      const profileData = await profileResponse.json();
      console.log('Профиль пользователя:', profileData);

      // Сохраняем профиль в localStorage
      localStorage.setItem('user_profile', JSON.stringify(profileData));
      localStorage.setItem('id', profileData.id)
      localStorage.setItem('email', profileData.email)
      localStorage.setItem('username', profileData.username)
      localStorage.setItem('name', profileData.name)
      localStorage.setItem('description', profileData.description)
      localStorage.setItem('role', profileData.role);

      // Переход на главную страницу
      if (!localStorage.getItem('location_after_login')) {
        window.location.href = '#/home';
      }
      else {
        window.location.href = localStorage.getItem('location_after_login')
      }

    } catch (error) {
      console.error('Произошла ошибка:', error);
      setServerError(error.message);
    }
  } else {
    setErrors(validationResult.errors);
  }
};

  return (
    <div className="signup-container">
        <Navbar/>
      <div className="signup-box">
        <Link to="/" className="back-button">
          <svg id="close-svg" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="size-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </Link>
        <div className="signup-header">
          <div className="logo-wrapper">
            <Logo size="large" />
          </div>
          <h2>Log in to your account</h2>
          <p>
            Don't have an account?{' '}
            <Link to="/signup" className="link">
              Sign up
            </Link>
          </p>
          {serverError && <p className="server-error">{serverError}</p>}
        </div>

        <form className="signup-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="identifier" className="sr-only">Username</label>
            <input
              id="identifier"
              name="identifier"
              type="identifier"
              value={formData.identifier}
              onChange={handleChange}
              className={`form-input ${errors.identifier ? 'input-error' : ''}`}
              placeholder="Email address or username"
            />
            {errors.identifier && <p className="error-text">{errors.identifier}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="sr-only">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className={`form-input ${errors.password ? 'input-error' : ''}`}
              placeholder="Password"
            />
            {errors.password && <p className="error-text">{errors.password}</p>}
          </div>


          <button type="submit" className="submit-button">
            Log in
          </button>
        </form>
      </div>
    </div>
  );
};

export default LogInPage;
