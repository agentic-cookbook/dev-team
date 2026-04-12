# platform-windows — Specialities

- [background-tasks](background-tasks.md) — Use `BackgroundTask` with Windows App SDK for background execution; register tri
- [csharp-naming](csharp-naming.md) — PascalCase for types, methods, properties, public fields, constants, namespaces;
- [deep-linking](deep-linking.md) — Protocol activation via `<uap:Protocol>` declaration in `Package.appxmanifest`; 
- [dependency-injection](dependency-injection.md) — Constructor injection via `Microsoft.Extensions.DependencyInjection`; use interf
- [design-time-data](design-time-data.md) — Use `d:DataContext` and `d:DesignInstance` for XAML designer preview data; use X
- [fluent-design](fluent-design.md) — Use built-in WinUI 3 controls — they implement Fluent 2 natively; never custom-d
- [handoff-and-continuity-windows](handoff-and-continuity-windows.md) — Windows does not have a native Handoff equivalent — use deep links as universal 
- [high-dpi-display-scaling](high-dpi-display-scaling.md) — XAML layout uses effective pixels (epx) — scaling is automatic for XAML content;
- [msix-packaging](msix-packaging.md) — Use single-project MSIX packaging model; declare capabilities minimally in `Pack
- [native-controls](native-controls.md) — Use platform built-in frameworks before custom implementations; WinUI 3 controls
- [notifications-windows](notifications-windows.md) — Use `AppNotificationManager` + `AppNotificationBuilder` fluent API for local not
- [nullable-reference-types](nullable-reference-types.md) — Enable `<Nullable>enable</Nullable>` in all projects; treat warnings as design s
- [platform-compliance](platform-compliance.md) — 7 compliance checks — platform-design-language (Fluent Design), native-controls-
- [search-integration-windows](search-integration-windows.md) — Use Windows Search indexer with `ISearchManager` and property handlers; register
- [share-and-inter-app-data-windows](share-and-inter-app-data-windows.md) — Implement Share Contract (`DataTransferManager`) to send and receive content; re
- [shortcuts-and-automation-windows](shortcuts-and-automation-windows.md) — Protocol activation for automation entry points; command-line activation via `Ap
- [theming](theming.md) — WinUI 3 tri-state theming — Light, Dark, High Contrast; set app-level theme via 
- [windows-architecture](windows-architecture.md) — MVVM with CommunityToolkit.Mvvm — source-generated `ObservableObject`, `RelayCom
