import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/') }

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">AutoNova</Link>
        <div className="nav-links">
          <Link to="/">Главная</Link>
          <Link to="/cars">Автомобили</Link>

          {user?.role === 'CLIENT' && <Link to="/my-bookings">Мои бронирования</Link>}

          {['MANAGER', 'ADMIN'].includes(user?.role) && (
            <>
              <Link to="/manager/bookings">Бронирования</Link>
              <Link to="/analytics">Аналитика</Link>
            </>
          )}

          {['MANAGER', 'ADMIN', 'INSPECTOR'].includes(user?.role) && (
            <Link to="/fleet">Автопарк</Link>
          )}

          {user?.role === 'ADMIN' && <Link to="/admin/users">Пользователи</Link>}

          {user ? (
            <button onClick={handleLogout} className="btn-outline btn-sm">
              {user.first_name || user.username} · Выйти
            </button>
          ) : (
            <>
              <Link to="/login">Войти</Link>
              <Link to="/register" className="btn-primary btn-sm">Регистрация</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
