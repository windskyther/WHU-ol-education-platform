export const MOOD_OPTIONS = [
  { key: 'happy', label: '开心', emoji: '😊' },
  { key: 'studying', label: '学习中', emoji: '📚' },
  { key: 'slacking', label: '摆烂中', emoji: '🛌' },
  { key: 'focused', label: '专注中', emoji: '🎯' },
  { key: 'tired', label: '疲惫中', emoji: '😴' },
  { key: 'excited', label: '超开心', emoji: '🎉' },
  { key: 'coding', label: '写代码中', emoji: '💻' }
]

export function getMoodOption(moodKey) {
  return MOOD_OPTIONS.find((item) => item.key === moodKey) || MOOD_OPTIONS[0]
}

export function getMoodDisplay(moodKey) {
  const option = getMoodOption(moodKey)
  return {
    key: option.key,
    label: option.label,
    emoji: option.emoji,
    text: `${option.emoji} ${option.label}`
  }
}
