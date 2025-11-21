import React from 'react';
import './UserAvatar.scss';

const UserAvatar = ({ user, size = 'medium', onClick }) => {
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRandomColor = (str) => {
    const colors = [
      '#667eea', '#764ba2', '#f093fb', '#4facfe', 
      '#43e97b', '#38f9d7', '#ffecd2', '#fcb69f'
    ];
    const index = str.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  };

  return (
    <div 
      className={`user-avatar ${size} ${onClick ? 'clickable' : ''}`}
      style={{ backgroundColor: getRandomColor(user.name || user.email) }}
      onClick={onClick}
    >
      {user.avatar ? (
        <img src={user.avatar} alt={user.name} />
      ) : (
        <span className="avatar-initials">
          {getInitials(user.name || user.email)}
        </span>
      )}
    </div>
  );
};

export default UserAvatar;