import { useState } from 'react';
import './styles/signup.css';
import Navbar from './components/NavBar';
import { BiColor } from 'react-icons/bi';

const SignupConfirm = () => {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    const storedData = localStorage.getItem('signup_temp');
    if (!storedData) {
      setError('Signup information not found. Please start over.');
      setSubmitting(false);
      return;
    }

    const { name, username, password } = JSON.parse(storedData);

    fetch(`https://api.vote.vickz.ru/api/v2/confirm-register/${code}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, username, password }),
    })
      .then(response => {
        if (!response.ok) {
          return response.json().then(data => {
            throw new Error(data.msg || 'Invalid code or server error. Get a new code and try again');
          });
        }
        return response.json();
      })
      .then(result => {
        localStorage.setItem('id', result.id);
        localStorage.setItem('username', result.username);
        localStorage.setItem('avatar_url', result.avatar_url);
        localStorage.setItem('access_token', result.access_token);
        localStorage.setItem('refresh_token', result.refresh_token);
        localStorage.setItem('private_key', result.private_key)
        localStorage.setItem('name', name);

        localStorage.removeItem('signup_temp');
        window.location.href = '#/profile-setup';
      })
      .catch(err => {
        setError(err.message);
        setSubmitting(false);
      });
  };

  return (
    <div className="signup-container">
      <Navbar />
      <div className="signup-box">
        <h2>Enter Confirmation Code</h2>
        <p className="instruction">
          Press <b>/start</b> in the bot{' '}
          <a
            href="https://t.me/SecureVoteBlockchainBot"
            target="_blank"
            rel="noopener noreferrer"
            className='blue-link'

          >
            @SecureVoteBlockchainBot
          </a>{' '}
          and enter the received code below.
        </p>
        {error && <p className="server-error">{error}</p>}
        <form className="signup-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="code" className="sr-only">Code</label>
            <input
              id="code"
              name="code"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className={`form-input ${error ? 'input-error' : ''}`}
              placeholder="Enter code"
              disabled={submitting}
            />
          </div>
          <button type="submit" className="submit-button" disabled={submitting}>
            Sign up
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupConfirm;
