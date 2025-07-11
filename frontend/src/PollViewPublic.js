import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import apiRequest from './components/Requests';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from 'recharts';
import './styles/pollviewcreator.css';
import './styles/pollviewpublic.css';
import { FiArrowLeft } from 'react-icons/fi';
import Vote from './components/BlockChain';


const PollViewPublic = () => {
  const { poll_id } = useParams();
  const navigate = useNavigate();
  const [notifyMe, setNotifyMe] = useState(false);

  const [pollData, setPollData] = useState(null);
  const [selectedOption, setSelectedOption] = useState('');
  const [voting, setVoting] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [commentLoading, setCommentLoading] = useState(false);

  useEffect(() => {
    const fetchPoll = async () => {
      try {
        const response = await apiRequest({
          url: `https://api.vote.vickz.ru/api/v2/get-poll/${poll_id}`,
          method: 'GET',
          auth: true,
          retry: true
        });

        if (!response.ok) throw new Error('Failed to load poll');

        const data = await response.json();
        if (data.user_username === localStorage.getItem('username')){
          window.location.href = `/#/poll-view-creator/${poll_id}`
        }
        setPollData(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load poll');
      } finally {
        setLoading(false);
      }
    };

    fetchPoll();
  }, [poll_id]);

  const fetchComments = async () => {
    try {
      const res = await apiRequest({
        url: `https://api.vote.vickz.ru/api/v2/get-comments/${poll_id}`,
        method: 'GET',
        auth: true
      });

      if (!res.ok) throw new Error('Failed to fetch comments');

      const data = await res.json();
      setComments(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (pollData) fetchComments();
  }, [pollData]);

  const handleVote = async () => {
    if (!selectedOption) {
      setError('Please select an option');
      return;
    }

    Vote(poll_id, selectedOption)

    setVoting(true);
    setError('');

    try {
      const response = await apiRequest({
        url: `https://api.vote.vickz.ru/api/v2/vote/${poll_id}`,
        method: 'POST',
        body: selectedOption,
        params: {
          notification: notifyMe
        },
        auth: true
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.msg || 'Vote failed');
      }

      const updated = await response.json();
      setPollData(updated);
    } catch (err) {
      alert('Voted successfully');
      window.location.href = '/#/home';
    }
  };

  const handleCommentSubmit = async () => {
    if (!commentText.trim()) return;

    setCommentLoading(true);
    try {
      const res = await apiRequest({
        url: `https://api.vote.vickz.ru/api/v2/add-comment/${poll_id}`,
        method: 'POST',
        body: commentText,
        auth: true
      });

      if (!res.ok) throw new Error('Failed to post comment');

      setCommentText('');
      fetchComments();
    } catch (err) {
      console.error(err);
      alert('Failed to post comment');
    } finally {
      setCommentLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!pollData) return <div className="error">Poll not found</div>;
  if (pollData.user_username === localStorage.getItem('username')) {
    window.location.href = '/#/poll/' + pollData.id;
  }

  const {
    name,
    description,
    options,
    start_date,
    end_date,
    votes_count,
    is_voted,
    is_active,
    user_id,
    user_username
  } = pollData;

  const isPollClosed = !is_active;
  const pollStatus = isPollClosed ? 'Closed' : 'Active';

  const colors = ['#4F46E5', '#10B981', '#FACC15', '#F87171', '#60A5FA', '#F472B6'];

  const chartData = isPollClosed && typeof options === 'object'
    ? Object.entries(options).map(([option, count], idx) => ({
        name: option,
        value: count,
        color: colors[idx % colors.length]
      }))
    : [];

  return (
    <div className="main-layout">
      <Sidebar />
      <div className="poll-view-content">
        <button className="back-to-home-button" onClick={() => navigate(-1)}>
          <FiArrowLeft size={30} />
        </button>

        <div className="poll-header">
          <img className="poll-icon" onClick={() => {window.location.href = '/#/user/'+user_username}} src={`https://blockchain-pfps.s3.regru.cloud/${user_username}/avatar_${user_id}.png`} />
          <div>
            <div className="poll-author" onClick={() => {window.location.href = '/#/user/'+user_username}}>{user_username}</div>
            <h1 className="poll-title">{name}</h1>
          </div>
        </div>

        <p className="poll-description">{description || 'No description provided.'}</p>

        <div className="poll-stats">
          <div>Total Votes: <strong>{votes_count}</strong></div>
          <div>Status: <span className={`poll-status ${isPollClosed ? 'closed' : 'active'}`}>{pollStatus}</span></div>
          <div>Start Date: <strong>{new Date(start_date).toLocaleString()}</strong></div>
          <div>End Date: <strong>{new Date(end_date).toLocaleString()}</strong></div>
        </div>

        <div className="poll-body">
          {isPollClosed ? (
            <>
              <div className="options-list">
                {chartData.map((item, idx) => {
                  const percent = votes_count > 0 ? ((item.value / votes_count) * 100).toFixed(0) : 0;
                  return (
                    <div className="option-item" key={idx}>
                      <span className="option-color" style={{ backgroundColor: item.color }} />
                      <span>{item.name}</span>
                      <span><strong>{percent}%</strong></span>
                    </div>
                  );
                })}
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={chartData} dataKey="value" innerRadius={60} outerRadius={100}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : is_voted ? (
            <p className="already-voted-message">You have already voted in this poll.</p>
          ) : (
            <>
              <form className="options-form">
                {Array.isArray(options) && options.map((option, idx) => (
                  <label key={idx} className="option-radio">
                    <input
                      type="radio"
                      name="vote"
                      value={option}
                      onChange={() => setSelectedOption(option)}
                      checked={selectedOption === option}
                    />
                    {option}
                  </label>
                ))}
              </form>

              <div className="notification-checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={notifyMe}
                    onChange={() => setNotifyMe(!notifyMe)}
                  />
                  Notify me about this poll's result
                </label>
              </div>

              <button
                className="submit-button"
                onClick={handleVote}
                disabled={voting}
              >
                {voting ? 'Voting...' : 'Submit Vote'}
              </button>

              {error && <p className="error-text">{error}</p>}
            </>
          )}
        </div>

        {/* COMMENTS SECTION */}
        <div className="comments-section">
          <div className="comment-input">
            <textarea
              placeholder="Write a comment..."
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              rows={3}
            />
            <button onClick={handleCommentSubmit} disabled={commentLoading || !commentText.trim()}>
              {commentLoading ? 'Posting...' : 'Post Comment'}
            </button>
          </div>
          <h2>Comments: {comments.length}</h2>
          <div className="comments-list">
{comments.map((comment, i) => {
  const isMyComment = comment.user_username === localStorage.getItem('username');

  return (
    <div key={i} className="comment-item">
      <Link to={`/user/${comment.user_username}`}>
        <img
          src={`https://blockchain-pfps.s3.regru.cloud/${comment.user_username}/avatar_${comment.user_id}.png`}
          alt={comment.user_id}
          className="comment-avatar"
        />
      </Link>

      <div className="comment-body">
        <div className="comment-header">
          <Link to={`/user/${comment.user_username}`} className="black-link">
            <strong>{comment.user_username}</strong>
          </Link>
{comments.map((comment, i) => {
  const isMyComment = comment.user_username === localStorage.getItem('username');

  return (
    <div key={i} className="comment-item">
      <Link to={`/user/${comment.user_username}`}>
        <img
          src={`https://blockchain-pfps.s3.regru.cloud/${comment.user_username}/avatar_${comment.user_id}.png`}
          alt={comment.user_id}
          className="comment-avatar"
        />
      </Link>

      <div className="comment-body">
        <div className="comment-header">
          <Link to={`/user/${comment.user_username}`} className="black-link">
            <strong>{comment.user_username}</strong>
          </Link>

          {isMyComment && (
            <div className="comment-dropdown">
              <button className="comment-dropdown-toggle">⋮</button>
              <div className="comment-dropdown-menu">
                <button
                  onClick={async () => {
                    try {
                      const res = await apiRequest({
                        url: `https://api.vote.vickz.ru/api/v2/delete-comment/${comment.id}`,
                        method: 'DELETE',
                        auth: true
                      });

                      if (!res.ok) throw new Error('Failed to delete');

                      fetchComments(); // refresh comment list
                    } catch (err) {
                      alert('Ошибка при удалении комментария');
                    }
                  }}
                >
                  Delete this comment
                </button>
              </div>
            </div>
          )}
        </div>
        <p className="comment-text">{comment.content}</p>
      </div>
    </div>
  );
})}

        </div>
        <p className="comment-text">{comment.content}</p>
      </div>
    </div>
  );
})}

          </div>
        </div>
      </div>
    </div>
  );
};

export default PollViewPublic;
