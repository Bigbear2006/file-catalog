export function displayDate(date: Date) {
  return date.toLocaleDateString('ru', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function displayTime(date: Date) {
  return date.toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
}

export function displayDateTime(date: Date, { sep }: { sep: string }) {
  return `${displayDate(date)}${sep}${displayTime(date)}`
}
