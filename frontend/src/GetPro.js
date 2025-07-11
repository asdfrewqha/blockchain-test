import React from 'react';
import Swal from 'sweetalert2';
import Sidebar from './components/Sidebar';
import apiRequest from './components/Requests';
import './styles/getpro.css';

const ProSubscribePage = () => {
  const handleSubscribe = async () => {
    try {
      const response = await apiRequest({
        url: 'https://api.vote.vickz.ru/api/v2/get-pro-subscribe',
        method: 'POST',
        auth: true,
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('role', 'PRO')
        Swal.fire({
          icon: 'success',
          title: 'You are now Pro!',
          text: data.message || 'You will now receive detailed PDF reports after each poll.',
        });
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Subscription failed',
          text: data.message || 'Something went wrong. Please try again later.',
        });
      }
    } catch (error) {
      Swal.fire({
        icon: 'error',
        title: 'Network Error',
        text: 'Could not connect to server.',
      });
    }
  };

  return (
    <div className="main-layout">
      <Sidebar />
      <div className="profile-content">
        <div className="pro-header">
          <h2>Upgrade to <span className="highlight">Pro</span></h2>
          <p>
            Get in-depth PDF analytics for your polls automatically after they close.
            These reports include vote distributions, participation trends, option comparisons,
            and more — perfect for sharing or reviewing performance.
          </p>
          <button className="get-pro-button" onClick={handleSubscribe}>
            Get Pro
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProSubscribePage;
