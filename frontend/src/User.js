import React, { useEffect, useState } from 'react';
import './styles/user.css';
import Sidebar from "./components/Sidebar";
import { Link, useParams } from 'react-router-dom';
import apiRequest from './components/Requests';

const UserPage = () => {
  const { username } = useParams();
  const [polls, setPolls] = useState([]);
  const [userInfo, setUserInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('polls');

  const avatarUrl = userInfo.id
    ? `https://blockchain-pfps.s3.regru.cloud/${userInfo.username}/avatar_${userInfo.id}.png`
    : '';

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const [pollsResponse, userResponse] = await Promise.all([
          apiRequest({
            url: `https://api.vote.vickz.ru/api/v2/get-polls-by-username/${username}`,
            method: 'GET',
            auth: true,
          }),
          apiRequest({
            url: `https://api.vote.vickz.ru/api/v2/get-user/${username}`,
            method: 'GET',
            auth: true,
          }),
        ]);

        if (!pollsResponse.ok || !userResponse.ok) {
          throw new Error('Failed to fetch data');
        }

        const pollsData = await pollsResponse.json();
        const userData = await userResponse.json();

        setPolls(pollsData);
        setUserInfo(userData);
      } catch (error) {
        console.error('Error loading user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
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

  const renderPollCards = () => {
    if (loading) return <p>Loading...</p>;
    if (polls.length === 0) return <p>No polls to display.</p>;

    return polls.map((poll) => {
      const isPollOpen = isOpen(poll.end_date);

      return (
        <Link
          to={`/poll-view-creator/${poll.id}`}
          key={poll.id}
          className="vote-card"
        >
          <div className="vote-header">
            <div className="vote-user">
              <img src={avatarUrl} alt="User" className="vote-avatar" />
              <span className="vote-username">{poll.user_username || username}</span>
            </div>
            <span className={`vote-status ${isPollOpen ? 'open' : 'closed'}`}>
              {isPollOpen ? 'Open' : 'Closed'}
            </span>
          </div>
          <div className="vote-body">
            <h3>{poll.name}</h3>
            <p>Total votes: {poll.votes ?? poll.votes_count}</p>
            <div className="vote-results">{renderOptions(poll.options)}</div>
          </div>
        </Link>
      );
    });
  };

  return (
    <div className="main-layout">
      <Sidebar />
      <div className="profile-content">
        <div className="profile-header">
          <img src={avatarUrl} alt="Avatar" className="profile-avatar" />
          <div className="profile-info">
            <h2>{userInfo.username || username}</h2>
            <p>{userInfo.description}</p>
            <div className="profile-stats">
              <div>Created: {polls.length}</div>
            </div>
          </div>
        </div>

        <div className="profile-tabs">
          <button
            className={`tab-btn ${activeTab === 'polls' ? 'active' : ''}`}
            onClick={() => setActiveTab('polls')}
          >
            Polls of {username}
          </button>
        </div>

        {activeTab === 'polls' && (
          <div className="votes-grid">{renderPollCards()}</div>
        )}
      </div>
    </div>
  );
};

export default UserPage;
