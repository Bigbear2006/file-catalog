import type { AxiosResponse } from 'axios'

export function displayRetryAfterSeconds(rsp: AxiosResponse) {
  const retryAfter = parseInt(rsp.headers['retry-after'])
  return Number.isNaN(retryAfter)
    ? ''
    : ` Попробуйте снова через ${retryAfter} секунд`
}

export function displayRetryAfter(rsp: AxiosResponse): string {
  const retryAfterStr = displayRetryAfterSeconds(rsp)

  if (rsp.status == 429) {
    return `Слишком много запросов, скачивание остановлено.${retryAfterStr}`
  }

  if (rsp.status === 403) {
    return `Вы заблокированы за слишком частые запросы.${retryAfterStr}`
  }

  return retryAfterStr
}
