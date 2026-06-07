import { useState, useEffect } from 'react'
import { api } from '../api'

const ROLES = [
  { value: 'ADMIN',     label: 'Администратор' },
  { value: 'MANAGER',   label: 'Менеджер' },
  { value: 'CLIENT',    label: 'Клиент' },
  { value: 'INSPECTOR', label: 'Инспектор автопарка' },
]

export function StaffUsers() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.users().then(setUsers).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const updateRole = async (profileId, role) => {
    try { await api.updateUserRole(profileId, role); load() }
    catch (err) { alert(err.message) }
  }

  if (loading) return <div className="loading">Загрузка...</div>

  return (
    <div className="page">
      <h1>Пользователи</h1>
      <div className="table-wrapper">
        <table className="table">
          <thead>
            <tr>
              <th>ФИО (логин)</th>
              <th>Email</th>
              <th>Телефон</th>
              <th>Роль</th>
              <th>Изменить роль</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td>{u.first_name} {u.last_name} <span className="text-muted">({u.username})</span></td>
                <td>{u.email}</td>
                <td>{u.phone}</td>
                <td>
                  <span className={`role-badge role-${u.role.toLowerCase()}`}>{u.role_display}</span>
                </td>
                <td>
                  <select value={u.role} onChange={e => updateRole(u.id, e.target.value)} className="select select-sm">
                    {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
