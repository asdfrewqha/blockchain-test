import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { FiArrowLeft, FiShare2, FiTrash } from 'react-icons/fi';
import Swal from 'sweetalert2';
import apiRequest from './components/Requests';
import './styles/pollviewcreator.css';
import './styles/pollviewpublic.css'; // подключаем стили для комментариев

const PollViewCreator = () => {
  const navigate = useNavigate();
  const { poll_id } = useParams();
  const [pollData, setPollData] = useState(null);
  const [chartType, setChartType] = useState('pie');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Состояния для комментариев
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

        if (!response.ok) throw new Error('Failed to load poll data');

        const data = await response.json();
        const currentUsername = localStorage.getItem('username');

        if (data.user_username !== currentUsername) {
          window.location.href = `/#/poll/${data.id}`;
          return;
        }

        if (!data.options || typeof data.options !== 'object') {
          throw new Error('Invalid poll format');
        }

        setPollData(data);
      } catch (err) {
        console.error(err);
        setError('Could not load poll data');
      } finally {
        setLoading(false);
      }
    };

    fetchPoll();
  }, [poll_id, navigate]);

  // Получение комментариев
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

  // Получаем комментарии при загрузке опроса
  useEffect(() => {
    if (pollData) fetchComments();
  }, [pollData]);

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
  if (!pollData || !pollData.options) return <div className="error">Poll not found or no data</div>;

  const data = Object.entries(pollData.options).map(([name, value], idx) => {
    const colors = ['#4F46E5', '#10B981', '#FACC15', '#F87171', '#60A5FA', '#F472B6'];
    return {
      name,
      value,
      color: colors[idx % colors.length],
    };
  });

  const totalVotes = data.reduce((sum, item) => sum + item.value, 0);
  const isPollClosed = new Date(pollData.end_date) < new Date();
  const pollStatus = isPollClosed ? 'Closed' : 'Active';

  const handleShare = () => {
    const link = `${window.location.origin}/#/poll/${poll_id}`;
    Swal.fire({
      title: 'Share this poll',
      html: `
        <input id="share-link" class="swal2-input" value="${link}" readonly>
        <button id="copy-link-btn" class="swal2-confirm swal2-styled">Copy Link</button>
      `,
      showConfirmButton: false,
      didOpen: () => {
        document.getElementById('copy-link-btn').onclick = () => {
          navigator.clipboard.writeText(link);
          Swal.close();
          Swal.fire('Copied!', '', 'success');
        };
      }
    });
  };

  const handleEndPoll = async () => {
    const confirm = await Swal.fire({
      title: 'End Poll Early?',
      text: 'This action is irreversible.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, end it',
      cancelButtonText: 'Cancel',
    });

    if (confirm.isConfirmed) {
      try {
        const res = await apiRequest({
          url: `https://api.vote.vickz.ru/api/v2/end-poll/${poll_id}`,
          method: 'POST',
          auth: true,
        });

        if (!res.ok) throw new Error('Failed to end poll');

        Swal.fire('Poll closed successfully', '', 'success').then(() => {
          window.location.reload();
        });
      } catch (err) {
        Swal.fire('Error', err.message, 'error');
      }
    }
  };

  const handleDeletePoll = async () => {
  const confirm = await Swal.fire({
    title: 'Delete Poll?',
    text: 'This action is irreversible. All data will be lost.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Yes, delete it',
    cancelButtonText: 'Cancel',
  });

  if (confirm.isConfirmed) {
    try {
      const res = await apiRequest({
        url: `https://api.vote.vickz.ru/api/v2/delete-poll/${poll_id}`,
        method: 'DELETE',
        auth: true,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || 'Failed to delete poll');
      }

      Swal.fire('Poll deleted', '', 'success').then(() => {
        navigate('/home'); // или куда ты хочешь направить пользователя
      });
    } catch (err) {
      Swal.fire('Error', err.message, 'error');
    }
  }
};



  return (
    <div className="main-layout">
      <Sidebar />
      <div className="poll-view-content">
        <button className="back-to-home-button" onClick={() => navigate(-1)}>
          <FiArrowLeft size={30} />
        </button>

        <div className="poll-header">
          <img className="poll-icon" src={`https://blockchain-pfps.s3.regru.cloud/${pollData.user_username}/avatar_${pollData.user_id}.png`} />
          <div>
            <div className="poll-author">{pollData.user_username}</div>
            <h1 className="poll-title">{pollData.name}</h1>
          </div>
        </div>

        <p className="poll-description">{pollData.description || 'No description provided.'}</p>

        <div className="poll-stats">
          <div>Total Votes: <strong>{totalVotes}</strong></div>
          <div>Status: <span className={`poll-status ${isPollClosed ? 'closed' : 'active'}`}>{pollStatus}</span></div>
          <div>Start Date: <strong>{new Date(pollData.start_date).toLocaleString()}</strong></div>
          <div>End Date: <strong>{new Date(pollData.end_date).toLocaleString()}</strong></div>
        </div>

        <div className="poll-body">
          <div className="options-list">
            {data.map((option, i) => (
              <div className="option-item" key={i}>
                <span className="option-color" style={{ backgroundColor: option.color }} />
                <span>{option.name}</span>
                <span><strong>{totalVotes > 0 ? ((option.value / totalVotes) * 100).toFixed(0) : 0}%</strong></span>
              </div>
            ))}
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              {chartType === 'pie' ? (
                <PieChart>
                  <Pie data={data} dataKey="value" innerRadius={60} outerRadius={100}>
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              ) : (
                <BarChart data={data}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value">
                    {data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </div>

        <div className="controls">
          <div className="view-switch">
            <button onClick={() => setChartType('pie')} className={chartType === 'pie' ? 'active' : ''}>Pie</button>
            <button onClick={() => setChartType('bar')} className={chartType === 'bar' ? 'active' : ''}>Bar</button>
          </div>

          <div className="actions">
            <button className="export-button" onClick={handleShare}>
              <FiShare2 style={{ marginRight: 6 }} />
              Share
            </button>

            {!isPollClosed && (
              <button className="export-button" style={{ backgroundColor: '#ef4444' }} onClick={handleEndPoll}>
                End Poll Early
              </button>
            )}
            <button
              className="export-button"
              style={{ backgroundColor: '#b91c1c' }}
              onClick={handleDeletePoll}
            >
              <FiTrash style={{ marginRight: 6 }} />
              Delete Poll
            </button>

          </div>
        </div>

        {/* Комментарии */}
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
        </div>
      </div>
    </div>
  );
};

export default PollViewCreator;
