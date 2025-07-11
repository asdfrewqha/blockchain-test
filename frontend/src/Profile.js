import React, { useEffect, useState } from 'react';
import './styles/profile.css';
import Sidebar from "./components/Sidebar";
import { Link } from 'react-router-dom';
import apiRequest from './components/Requests';

const ProfilePage = () => {
  const [polls, setPolls] = useState([]);
  const [votedPolls, setVotedPolls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('your');

  const username = localStorage.getItem('username');
  const userId = localStorage.getItem('id');
  const name = localStorage.getItem('name');
  const description = localStorage.getItem('description');
  const avatarUrl = `https://blockchain-pfps.s3.regru.cloud/${username}/avatar_${userId}.png`;

  useEffect(() => {
    const fetchPolls = async () => {
      try {
        const [createdResponse, votedResponse] = await Promise.all([
          apiRequest({
            url: `https://api.vote.vickz.ru/api/v2/get-polls-by-username/${username}`,
            method: 'GET',
            auth: true,
          }),
          apiRequest({
            url: 'https://api.vote.vickz.ru/api/v2/get-my-votes',
            method: 'GET',
            auth: true,
          }),
        ]);

        if (!createdResponse.ok || !votedResponse.ok) {
          throw new Error('Failed to fetch polls');
        }

        const createdPolls = await createdResponse.json();
        const voted = await votedResponse.json();

        setPolls(createdPolls);
        setVotedPolls(voted);
      } catch (error) {
        console.error('Error loading polls:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPolls();
  }, [username]);

  const formatPollOptions = (options) => {
    const totalVotes = Object.values(options).reduce((sum, val) => sum + val, 0);
    const colorClasses = ['yellow', 'green', 'blue', 'red', 'purple', 'pink', 'orange'];

    return Object.entries(options).map(([option, count], index) => {
      const percent = totalVotes === 0 ? 0 : Math.round((count / totalVotes) * 100);
      const colorClass = colorClasses[index % colorClasses.length];

      return (
        <div key={option} className={`vote-option ${colorClass}`}>
          {option} – {percent}%
        </div>
      );
    });
  };

  const renderOptions = (options) => {
    const colorClasses = ['yellow', 'green', 'blue', 'red', 'purple', 'pink', 'orange'];

    if (Array.isArray(options)) {
      return options.map((option, index) => (
        <div
          key={option}
          className={`vote-option ${colorClasses[index % colorClasses.length]}`}
        >
          {option}
        </div>
      ));
    } else if (typeof options === 'object' && options !== null) {
      return formatPollOptions(options);
    } else {
      return <div className="vote-option">Invalid options format</div>;
    }
  };

  const isOpen = (endDate) => new Date(endDate) > new Date();

  const renderPollCards = (pollList, type) => {
    if (loading) return <p>Loading...</p>;
    if (pollList.length === 0) return <p>No polls to display.</p>;

    return pollList.map((poll) => {
      const isPollOpen = isOpen(poll.end_date);

      return (
        <Link
          to={type === 'participated' ? `/poll/${poll.id}` : `/poll-view-creator/${poll.id}`}
          key={poll.id}
          className="vote-card"
        >
          <div className="vote-header">
            <div className="vote-user">
              <img src={`https://blockchain-pfps.s3.regru.cloud/${poll.user_username}/avatar_${poll.user_id}.png`} alt="User" className="vote-avatar" />
              <span className="vote-username">{poll.user_username || username}</span>
            </div>
            <span className={`vote-status ${isPollOpen ? 'open' : 'closed'}`}>
              {isPollOpen ? 'Open' : 'Closed'}
            </span>
          </div>
          <div className="vote-body">
            <h3>{poll.name}</h3>
            <p>Total votes: {poll.votes ?? poll.votes_count}</p>
            <div className="vote-results">
              {renderOptions(poll.options)}
            </div>
          </div>
        </Link>
      );
    });
  };

  return (
    <div className='main-layout'>
      <Sidebar />
      <div className="profile-content">
      <div className="profile-header">
        <img src={avatarUrl} alt="Avatar" className="profile-avatar" />
        <div className="profile-info">
          <h2>{name}</h2>
          <p>{description}</p>
          <div className="profile-stats">
            <div>Created: {polls.length}</div>
            <div>Participated: {votedPolls.length}</div>
          </div>
        </div>
        <div className="profile-header-left">
          {localStorage.getItem('role')==='USER' ? <button className="get-pro-button" onClick={() => {window.location.href = '/#/get-pro'}}>Get Pro</button> : <p className='get-pro-button text'>Pro user</p>}
        </div>
      </div>


        <div className="profile-tabs">
          <button
            className={`tab-btn ${activeTab === 'your' ? 'active' : ''}`}
            onClick={() => setActiveTab('your')}
          >
            Your Polls
          </button>
          <button
            className={`tab-btn ${activeTab === 'participated' ? 'active' : ''}`}
            onClick={() => setActiveTab('participated')}
          >
            Participated
          </button>
        </div>

        <div className="votes-grid">
          {activeTab === 'your' && (
            <>
              <Link to='/new-poll'>
                <div className="vote-card create-card">
                  <div className="create-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <div className="create-text">Create Poll</div>
                </div>
              </Link>
              {renderPollCards(polls, 'your')}
            </>
          )}

          {activeTab === 'participated' && renderPollCards(votedPolls, 'participated')}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
