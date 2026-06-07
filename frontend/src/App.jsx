import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { Navbar } from './components/Navbar'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Home } from './pages/Home'
import { Cars } from './pages/Cars'
import { CarDetail } from './pages/CarDetail'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { MyBookings } from './pages/MyBookings'
import { ManagerBookings } from './pages/ManagerBookings'
import { FleetStatus } from './pages/FleetStatus'
import { StaffUsers } from './pages/StaffUsers'
import { Analytics } from './pages/Analytics'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Navbar />
        <main>
          <Routes>
            <Route path="/"         element={<Home />} />
            <Route path="/cars"     element={<Cars />} />
            <Route path="/cars/:id" element={<CarDetail />} />
            <Route path="/login"    element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route path="/my-bookings" element={
              <ProtectedRoute roles={['CLIENT']}>
                <MyBookings />
              </ProtectedRoute>
            } />
            <Route path="/manager/bookings" element={
              <ProtectedRoute roles={['MANAGER', 'ADMIN']}>
                <ManagerBookings />
              </ProtectedRoute>
            } />
            <Route path="/fleet" element={
              <ProtectedRoute roles={['MANAGER', 'ADMIN', 'INSPECTOR']}>
                <FleetStatus />
              </ProtectedRoute>
            } />
            <Route path="/admin/users" element={
              <ProtectedRoute roles={['ADMIN']}>
                <StaffUsers />
              </ProtectedRoute>
            } />
            <Route path="/analytics" element={
              <ProtectedRoute roles={['MANAGER', 'ADMIN']}>
                <Analytics />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </AuthProvider>
    </BrowserRouter>
  )
}
