import { useState } from 'react'
import { format } from 'date-fns'
import { useMapStore } from '@/store/mapStore'

const DateRangePicker = () => {
  const { startDate, endDate, setDateRange } = useMapStore()
  const [isOpen, setIsOpen] = useState(false)
  const [localStartDate, setLocalStartDate] = useState(startDate)
  const [localEndDate, setLocalEndDate] = useState(endDate)

  const toggleOpen = () => {
    setIsOpen(!isOpen)
  }

  const handleApply = () => {
    setDateRange(localStartDate, localEndDate)
    setIsOpen(false)
  }

  const handleCancel = () => {
    setLocalStartDate(startDate)
    setLocalEndDate(endDate)
    setIsOpen(false)
  }

  // Format dates for display
  const formattedStartDate = format(new Date(startDate), 'MMM d, yyyy')
  const formattedEndDate = format(new Date(endDate), 'MMM d, yyyy')

  return (
    <div className="relative">
      <button
        onClick={toggleOpen}
        className="bg-white rounded-lg shadow-md px-4 py-2 flex items-center space-x-2"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 text-gray-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <span>
          {formattedStartDate} - {formattedEndDate}
        </span>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 bg-white rounded-lg shadow-lg p-4 z-10 w-72">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={localStartDate}
              onChange={(e) => setLocalStartDate(e.target.value)}
              className="w-full p-2 border rounded"
              min="2020-01-01"
              max={localEndDate}
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={localEndDate}
              onChange={(e) => setLocalEndDate(e.target.value)}
              className="w-full p-2 border rounded"
              min={localStartDate}
              max="2022-12-31"
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              onClick={handleCancel}
              className="px-3 py-1 border rounded text-gray-700 hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DateRangePicker
