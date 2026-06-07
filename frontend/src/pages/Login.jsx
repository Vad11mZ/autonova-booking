import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const REDIRECT = { CLIENT: '/my-bookings', MANAGER: '/manager/bookings', ADMIN: '/manager/bookings', INSPECTOR: '/fleet' }

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const user = await login({ username, password })
      navigate(REDIRECT[user.role] || '/')
    } catch (err) { setError(err.message) }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Вход в AutoNova</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Логин</label>
            <input value={username} onChange={e => setUsername(e.target.value)} className="input" required autoFocus />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="input" required />
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <button type="submit" className="btn-primary w-full">Войти</button>
        </form>
        <p className="auth-footer">Нет аккаунта? <Link to="/register">Зарегистрироваться</Link></p>
      </div>
    </div>
  )
}
