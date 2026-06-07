import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '', password: '', first_name: '', last_name: '',
    email: '', phone: '', birth_date: '', license_years: 0, driver_license: '',
  })
  const [error, setError] = useState('')

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register({ ...form, license_years: Number(form.license_years) })
      navigate('/my-bookings')
    } catch (err) { setError(err.message) }
  }

  return (
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <h2>Регистрация клиента</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Имя</label>
              <input value={form.first_name} onChange={set('first_name')} className="input" required />
            </div>
            <div className="form-group">
              <label>Фамилия</label>
              <input value={form.last_name} onChange={set('last_name')} className="input" required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Логин</label>
              <input value={form.username} onChange={set('username')} className="input" required />
            </div>
            <div className="form-group">
              <label>Пароль</label>
              <input type="password" value={form.password} onChange={set('password')} className="input" required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={set('email')} className="input" />
            </div>
            <div className="form-group">
              <label>Телефон</label>
              <input value={form.phone} onChange={set('phone')} className="input" placeholder="+7 900 000-00-00" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Дата рождения</label>
              <input type="date" value={form.birth_date} onChange={set('birth_date')} className="input" />
            </div>
            <div className="form-group">
              <label>Стаж вождения (лет)</label>
              <input type="number" min="0" value={form.license_years} onChange={set('license_years')} className="input" />
            </div>
          </div>
          <div className="form-group">
            <label>Номер водительского удостоверения</label>
            <input value={form.driver_license} onChange={set('driver_license')} className="input" />
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <button type="submit" className="btn-primary w-full">Зарегистрироваться</button>
        </form>
        <p className="auth-footer">Уже есть аккаунт? <Link to="/login">Войти</Link></p>
      </div>
    </div>
  )
}
