const BASE = '/api'

async function request(path, options = {}) {
  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })

  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || JSON.stringify(data))
  return data
}

export const api = {
  login:    (body) => request('/auth/login',    { method: 'POST', body: JSON.stringify(body) }),
  register: (body) => request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  me:       ()     => request('/auth/me'),

  stats:        ()       => request('/stats'),
  cars:         (p = {}) => request('/cars?' + new URLSearchParams(p)),
  categories:   ()       => request('/cars/categories'),
  car:          (id)     => request(`/cars/${id}`),
  availability: (id, s, e) => request(`/cars/${id}/availability?start_date=${s}&end_date=${e}`),

  createBooking: (body) => request('/bookings',          { method: 'POST', body: JSON.stringify(body) }),
  myBookings:    ()     => request('/bookings/my'),
  cancelBooking: (id)   => request(`/bookings/${id}/cancel`, { method: 'POST' }),

  managerBookings: (status = '') => request(`/manager/bookings${status ? '?status=' + status : ''}`),
  bookingAction:   (id, body)    => request(`/manager/bookings/${id}/action`, { method: 'POST', body: JSON.stringify(body) }),

  fleet:           ()          => request('/fleet'),
  updateCarStatus: (id, status) => request(`/fleet/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  users:          ()              => request('/admin/users'),
  updateUserRole: (profileId, role) => request(`/admin/users/${profileId}/role`, { method: 'PATCH', body: JSON.stringify({ role }) }),

  analytics: () => request('/analytics'),
}
