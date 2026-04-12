# platform-android — Specialities

- [background-tasks](background-tasks.md) — Use `WorkManager` for all deferrable background work — handles constraints, retr
- [deep-linking](deep-linking.md) — Android App Links (verified HTTP deep links) via `<intent-filter>` with `autoVer
- [font-scaling](font-scaling.md) — Layouts must not break at 2x font size; check `Configuration.fontScale` and test
- [handoff-and-continuity](handoff-and-continuity.md) — Use Firebase Dynamic Links or deep links that resolve in both native and web con
- [native-controls](native-controls.md) — Use platform built-in frameworks before custom implementations; WorkManager over
- [notifications](notifications.md) — Use `NotificationCompat.Builder` for backward-compatible notifications; declare 
- [platform-compliance](platform-compliance.md) — 7 compliance checks — platform-design-language (Material Design 3), native-contr
- [search-integration](search-integration.md) — Use Firebase App Indexing or `AppIndexingApi` for on-device search integration; 
- [share-and-inter-app-data](share-and-inter-app-data.md) — Declare `<intent-filter>` with `ACTION_SEND` and appropriate MIME types to recei
- [shortcuts-and-automation](shortcuts-and-automation.md) — Use `AppActions` for Google Assistant integration; support `Intent`-based automa
- [widgets-and-glanceable-surfaces](widgets-and-glanceable-surfaces.md) — Use Jetpack Glance with Compose-style APIs for home screen widgets; define widge
