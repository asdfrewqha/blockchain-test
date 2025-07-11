import { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from './components/Logo';
import { validateSignup } from './components/validation';
import './styles/signup.css';
import Navbar from './components/NavBar';

const SignupPage = () => {

  const [formData, setFormData] = useState({
    email: '',
    username: '',
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
  setServerError('');
  setErrors({});

  const validationResult = validateSignup(formData);

  if (validationResult.isValid) {
    try {
      const response = await fetch(`https://api.vote.vickz.ru/api/v2/check-username/${formData.username}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.msg || 'Username check failed');
      }

      // Успешно: сохраняем и переходим к подтверждению
      localStorage.setItem('signup_temp', JSON.stringify(formData));
      window.location.href = '#/signup-confirm';
    } catch (error) {
      console.error('Ошибка при проверке username:', error);
      setServerError(error.message);
    }
  } else {
    setErrors(validationResult.errors);
  }
};



  return (
    <div className="signup-container">
      <Navbar />
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
          <h2>Create your account</h2>
          <p className='login-suggest'>
            Already have an account?{' '}
            <Link to="/login" className="link">
              Log in
            </Link>
          </p>
          {serverError && <p className="server-error">{serverError}</p>}
        </div>

        <form className="signup-form" onSubmit={handleSubmit}>


          <div className="form-group">
            <label htmlFor="username" className="sr-only">Username</label>
            <input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              className={`form-input ${errors.username ? 'input-error' : ''}`}
              placeholder="Username"
            />
            {errors.username && <p className="error-text">{errors.username}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="name" className="sr-only">Name</label>
            <input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              className={`form-input ${errors.name ? 'input-error' : ''}`}
              placeholder="Name"
            />
            {errors.username && <p className="error-text">{errors.username}</p>}
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
            Sign up
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;
