
import TimetableGrid from './components/TimetableGrid';
import { Calendar } from 'lucide-react';
import Button from './components/Button';
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
        <div className="topbar-actions">
          <span className="topbar-greeting">Xin chào, Giảng viên</span>
          <Button variant="ghost" className="topbar-logout">
            Đăng xuất
          </Button>
        </div>
      </header>
      <main className="main-content">
        <TimetableGrid />
      </main>
    </div>
  );
}

export default App;
