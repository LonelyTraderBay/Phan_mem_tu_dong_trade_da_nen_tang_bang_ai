/**
 * Placeholder WebSocket client with reconnect / resume stubs.
 * Wire to NEXT_PUBLIC_WS_URL and real protocol later.
 */

export type WsClientState = "idle" | "connecting" | "open" | "closed";

export class WsClient {
  private url: string;
  private state: WsClientState = "idle";
  private socket: WebSocket | null = null;
  private lastResumeToken: string | null = null;

  constructor(url?: string) {
    this.url =
      url ?? process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";
  }

  getState(): WsClientState {
    return this.state;
  }

  /** Stub — open connection (not implemented). */
  connect(): void {
    this.state = "connecting";
    // TODO: create WebSocket, attach handlers
    this.state = "closed";
  }

  /** Stub — attempt reconnect after disconnect. */
  reconnect(): void {
    this.state = "connecting";
    // TODO: backoff + reconnect
    this.state = "closed";
  }

  /** Stub — resume stream using last token. */
  resume(token?: string): void {
    if (token) {
      this.lastResumeToken = token;
    }
    // TODO: send resume frame with this.lastResumeToken
    void this.lastResumeToken;
    void this.socket;
  }

  disconnect(): void {
    this.socket = null;
    this.state = "closed";
  }
}
