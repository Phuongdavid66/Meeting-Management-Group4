import React from 'react';
import TimetableGrid from './components/TimetableGrid';
import { Calendar } from 'lucide-react';
import './App.css';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <header className="topbar">
        <div className="topbar-brand">
          <Calendar size={24} color="var(--color-accent)" />
          ICTU <span>Meeting</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem' }}>Xin chào, Giảng viên</span>
          <button className="btn btn-ghost" style={{ borderColor: 'var(--color-gray-600)', color: 'var(--color-white)' }}>
            Đăng xuất
          </button>
        </div>
      </header>
      <main className="main-content">
        <TimetableGrid />
      </main>
    </div>
  );
}

export default App;
