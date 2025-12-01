import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Collaboration.css';

const Collaboration = ({ documentId, userId, token }) => {
  const [comments, setComments] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchComments();
    fetchNotifications();
  }, [documentId, userId]);

  const fetchComments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `/api/collaboration/comments/document/${documentId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setComments(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load comments');
    } finally {
      setLoading(false);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(
        `/api/collaboration/notifications/unread/${userId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNotifications(response.data);
    } catch (err) {
      console.error('Failed to fetch notifications');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    try {
      await axios.post(
        '/api/collaboration/comments',
        { user_id: userId, document_id: documentId, content: newComment },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewComment('');
      fetchComments();
    } catch (err) {
      setError('Failed to add comment');
    }
  };

  const handleResolveComment = async (commentId) => {
    try {
      await axios.put(
        `/api/collaboration/comments/${commentId}/resolve`,
        { resolved_by_id: userId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchComments();
    } catch (err) {
      setError('Failed to resolve comment');
    }
  };

  const handleMarkNotificationRead = async (notifId) => {
    try {
      await axios.put(
        `/api/collaboration/notifications/${notifId}/read`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchNotifications();
    } catch (err) {
      console.error('Failed to mark notification as read');
    }
  };

  return (
    <div className="collaboration-container">
      <div className="notifications-panel">
        <h3>Notifications ({notifications.length})</h3>
        {notifications.map(notif => (
          <div key={notif.id} className="notification-item">
            <span>{notif.message}</span>
            <button onClick={() => handleMarkNotificationRead(notif.id)}>Mark Read</button>
          </div>
        ))}
      </div>
      <div className="comments-panel">
        <h3>Comments ({comments.length})</h3>
        {error && <div className="error-message">{error}</div>}
        {loading ? <p>Loading...</p> : (
          <div className="comments-list">
            {comments.map(comment => (
              <div key={comment.id} className="comment-item">
                <p>{comment.content}</p>
                <button onClick={() => handleResolveComment(comment.id)}>Resolve</button>
              </div>
            ))}
          </div>
        )}
        <div className="add-comment">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add a comment..."
          />
          <button onClick={handleAddComment}>Post Comment</button>
        </div>
      </div>
    </div>
  );
};

export default Collaboration;
