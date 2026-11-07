import { useEffect } from 'react'

export function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = title ? `${title} · FinAccess Compass Rwanda` : 'FinAccess Compass Rwanda'
  }, [title])
}
