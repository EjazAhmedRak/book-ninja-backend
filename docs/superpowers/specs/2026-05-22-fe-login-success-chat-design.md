# FE Login + Login Success + Protected Chat Design

## Context
This design covers the first frontend implementation slice for Book Ninja in `apps/frontend`.

Goal for this slice:
- Establish a real route flow for authentication entry and post-login transition.
- Build a protected `/chat` page that includes a welcome banner above a chat window.
- Seed the chat window with an initial assistant message explaining available options.
- Keep chat interaction local-only for now (no backend `/chat` API wiring yet).

## Scope
In scope:
- Add client-side routing.
- Add a dedicated login page.
- Add a login-success transition page.
- Add auth validation for `/chat` using an in-memory token check.
- Add welcome banner and seeded assistant message on chat page.
- Add interactive local composer UI (input + send) without network calls.
- Add minimal tests for route behavior and local message flow.

Out of scope:
- Real Google OAuth integration.
- Backend token validation calls.
- SSE `/chat` streaming integration.
- Thread history, sidebar, and API hooks.
- Persistent auth storage.

## Route Architecture
Routes:
- `/login` (public)
- `/login-success` (public transitional)
- `/chat` (protected)

Flow:
1. User lands on `/login`.
2. Login success action sets token in in-memory auth store.
3. User is navigated to `/login-success`.
4. `/login-success` shows success confirmation briefly and auto-redirects to `/chat`.
5. `/chat` validates token:
- Token present: render chat experience.
- Token missing: redirect to `/login`.

## Component and File Plan
Planned additions/updates:
- `src/main.jsx`: bootstrap router.
- `src/AppRouter.jsx`: define route map and mount guarded/public routes.
- `src/store/useAuthStore.js`: in-memory auth store with `token`, `setToken`, `clearToken`.
- `src/components/ProtectedRoute.jsx`: route guard for auth-protected pages.
- `src/pages/LoginPage.jsx`: login entry page with a mock success action for this phase.
- `src/pages/LoginSuccessPage.jsx`: success flash + timed redirect.
- `src/pages/ChatPage.jsx`: welcome banner + chat window shell.
- `src/components/WelcomeBanner.jsx`: top banner content.
- `src/components/ChatWindow.jsx`: seeded assistant message + local message compose/send.

## Data Model (Local UI Only)
Local message shape:
- `id: string`
- `role: 'assistant' | 'user'`
- `content: string`
- `timestamp: string`

Seeded initial assistant message content will explain that users can:
- search books by title/author/topic
- ask for recommendations
- request ebook, audiobook, or purchase options

## State and Interaction Flow
### Login Page
- Renders login CTA.
- On simulated success:
1. set in-memory token
2. navigate to `/login-success`

### Login Success Page
- Renders success state.
- Starts redirect timer on mount.
- Navigates to `/chat` after short delay.
- Clears timer on unmount.

### Protected Chat
- `ProtectedRoute` checks `token` from auth store.
- Missing token redirects to `/login`.
- Present token renders chat page.

### Chat Window (Local)
- Initialize messages with one seeded assistant message.
- User types message and submits.
- Empty/whitespace submissions are ignored.
- Valid input appends user message to local list.
- No API call is made in this phase.

## Error Handling and Edge Cases
- Redirect timer cleanup to avoid stale navigation after unmount.
- Guard against duplicate redirect calls.
- Ignore empty/whitespace messages.
- Enforce frontend message input max length aligned with backend limit intent.
- Direct navigation to `/chat` without token always redirects to `/login`.

## Testing Plan
Minimum tests for this slice:
1. Route guard redirects `/chat` to `/login` when token is absent.
2. Login action writes token and routes to `/login-success`.
3. Login-success page auto-redirects to `/chat` after timer.
4. Chat page renders welcome banner and seeded assistant message.
5. Sending non-empty input appends user message locally.
6. Empty input does not append a message.

## Technical Decisions
- Use `react-router-dom` now to avoid migration from temporary state-based navigation.
- Use in-memory auth store only (no `localStorage`) to match security guidance in frontend draft docs.
- Keep API integration deferred to protect momentum and isolate this milestone to route/auth/UI shell.

## Acceptance Criteria
- App supports `/login`, `/login-success`, and protected `/chat` routes.
- `/chat` cannot be accessed without token.
- Login flow transitions through `/login-success` and reaches `/chat`.
- Chat UI includes welcome banner and seeded assistant message.
- Input/send is interactive with local-only message updates.
- Initial test suite for this scope passes.
