import { Component, type ErrorInfo, type ReactNode } from 'react'

type State = { error: Error | null }

/** Keeps a rendering bug on one page from blanking the whole app. Give it a `key` to reset on navigation. */
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UI error', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="banner error" role="alert">
          <p>
            <strong>Something went wrong displaying this page.</strong>
          </p>
          <p className="small">{this.state.error.message}</p>
          <button type="button" className="cta" onClick={() => this.setState({ error: null })}>
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
