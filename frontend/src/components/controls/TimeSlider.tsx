import { useState, useEffect, useMemo } from 'react'
import { format, addDays, differenceInDays, parseISO } from 'date-fns'
import { useMapStore } from '@/store/mapStore'

const TimeSlider = () => {
  const { startDate, endDate, currentDate, setCurrentDate } = useMapStore()

  // Calculate the number of days in the range
  const dayCount = useMemo(() => {
    return differenceInDays(parseISO(endDate), parseISO(startDate)) + 1
  }, [startDate, endDate])

  // Calculate the current day index (0-based)
  const currentDayIndex = useMemo(() => {
    return differenceInDays(parseISO(currentDate), parseISO(startDate))
  }, [currentDate, startDate])

  // State for animation
  const [isPlaying, setIsPlaying] = useState(false)
  const [playSpeed, setPlaySpeed] = useState(1000) // ms per day

  // Generate array of all dates in range for display
  const dateArray = useMemo(() => {
    const dates = []
    let currentDateObj = parseISO(startDate)
    const endDateObj = parseISO(endDate)

    while (currentDateObj <= endDateObj) {
      dates.push(format(currentDateObj, 'yyyy-MM-dd'))
      currentDateObj = addDays(currentDateObj, 1)
    }

    return dates
  }, [startDate, endDate])

  // Handle slider change
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const index = parseInt(e.target.value)
    setCurrentDate(dateArray[index])
  }

  // Handle play/pause
  const togglePlay = () => {
    setIsPlaying(!isPlaying)
  }

  // Animation effect
  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      const currentIndex = dateArray.indexOf(currentDate)
      const nextIndex = (currentIndex + 1) % dateArray.length
      setCurrentDate(dateArray[nextIndex])
    }, playSpeed)

    return () => clearInterval(interval)
  }, [isPlaying, playSpeed, dateArray, setCurrentDate, currentDate])

  // Format current date for display
  const formattedCurrentDate = format(parseISO(currentDate), 'MMMM d, yyyy')

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center">
          <button
            onClick={togglePlay}
            className="mr-2 w-8 h-8 flex items-center justify-center rounded-full bg-blue-500 text-white hover:bg-blue-600"
          >
            {isPlaying ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" />
                <rect x="14" y="4" width="4" height="16" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5,3 19,12 5,21" />
              </svg>
            )}
          </button>
          <select
            value={playSpeed}
            onChange={(e) => setPlaySpeed(parseInt(e.target.value))}
            className="text-sm p-1 border rounded"
          >
            <option value="2000">0.5x Speed</option>
            <option value="1000">1x Speed</option>
            <option value="500">2x Speed</option>
            <option value="250">4x Speed</option>
          </select>
        </div>
        <div className="font-medium">{formattedCurrentDate}</div>
      </div>

      <div className="flex items-center">
        <span className="text-xs text-gray-500 mr-2">{format(parseISO(startDate), 'MMM d')}</span>
        <input
          type="range"
          min="0"
          max={dayCount - 1}
          value={currentDayIndex}
          onChange={handleSliderChange}
          className="flex-grow"
        />
        <span className="text-xs text-gray-500 ml-2">{format(parseISO(endDate), 'MMM d')}</span>
      </div>
    </div>
  )
}

export default TimeSlider
