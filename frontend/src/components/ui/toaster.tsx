import React from 'react'

// Simple toaster component for notifications
export const Toaster: React.FC = () => {
  return (
    <div id="toaster" className="fixed top-4 right-4 z-50">
      {/* Toasts will be dynamically added here */}
    </div>
  )
}

export default Toaster
