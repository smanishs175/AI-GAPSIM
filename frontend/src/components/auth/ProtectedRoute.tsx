import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import Loading from '@/components/ui/loading'

interface ProtectedRouteProps {
  children: ReactNode
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, token, isLoading } = useAuthStore()
  const location = useLocation()

  // If loading, show loading indicator
  if (isLoading) {
    return <Loading />
  }

  // If not authenticated, redirect to login
  if (!isAuthenticated || !token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // If authenticated, render children
  return <>{children}</>
}

export default ProtectedRoute
