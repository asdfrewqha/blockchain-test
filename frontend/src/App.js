import React from 'react';
import { HashRouter as Router, Route, Routes } from 'react-router-dom';
import WelcomePage from './Welcome.js';
import SignupPage from './SignUp.js';
import LogInPage from './Login.js';
import ProfilePage from './Profile.js';
import SearchPage from './Search.js';
import NotFoundPage from './NotFound.js';
import UserPage from './User.js';
import ProfileSetupPage from './ProfileSetup.js';
import UploadPage from './Upload.js';
import PollViewCreator from './PollViewCreator.js';
import SignupConfirm from './SignupConfirm.js';
import PollViewPublic from './PollViewPublic.js';
import SwaggerUIPage from './Swagger.js';
import SettingsPage from './Settings.js';
import TrendingPage from './Trending.js';
import ProSubscribePage from './GetPro.js';


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/signup-confirm" element={<SignupConfirm />} />
        <Route path="/login" element={<LogInPage />} />
        <Route path="/trending" element={<TrendingPage />} />
        <Route path="/profile-setup" element={<ProfileSetupPage />} />
        <Route path="/get-pro" element={<ProSubscribePage />} />
        <Route path="/poll-view-creator/:poll_id" element={<PollViewCreator />} />
        <Route path="/poll/:poll_id" element={<PollViewPublic />} />
        <Route path="/swagger" element={<SwaggerUIPage />} />
        <Route path="/home" element={<ProfilePage />} />
        <Route path="/new-poll" element={<UploadPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/user/:username" element={<UserPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
}

export default App;
