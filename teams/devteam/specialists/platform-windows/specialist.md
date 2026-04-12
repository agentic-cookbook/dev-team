# Windows Platform Specialist

## Role
WinUI 3, Fluent Design, MSIX packaging, High DPI/display scaling, MVVM with CommunityToolkit, theming (light/dark/high-contrast), .NET/C#, Narrator, UI Automation, platform integration.

## Persona
(coming)

## Cookbook Sources
- `guidelines/platform/windows/` (6 files: architecture, design-time-data, fluent-design, high-dpi-display-scaling, msix-packaging, theming)
- `guidelines/language/csharp/` (3 files: dependency-injection, naming, nullable-reference-types)
- `principles/native-controls.md`
- `guidelines/platform/` (8 files: background-tasks, deep-linking, handoff-and-continuity, notifications, search-integration, share-and-inter-app-data, shortcuts-and-automation, widgets-and-glanceable-surfaces)
- `compliance/platform-compliance.md`

## Manifest

- specialities/platform-windows/background-tasks.md
- specialities/platform-windows/csharp-naming.md
- specialities/platform-windows/deep-linking.md
- specialities/platform-windows/dependency-injection.md
- specialities/platform-windows/design-time-data.md
- specialities/platform-windows/fluent-design.md
- specialities/platform-windows/handoff-and-continuity-windows.md
- specialities/platform-windows/high-dpi-display-scaling.md
- specialities/platform-windows/msix-packaging.md
- specialities/platform-windows/native-controls.md
- specialities/platform-windows/notifications-windows.md
- specialities/platform-windows/nullable-reference-types.md
- specialities/platform-windows/platform-compliance.md
- specialities/platform-windows/search-integration-windows.md
- specialities/platform-windows/share-and-inter-app-data-windows.md
- specialities/platform-windows/shortcuts-and-automation-windows.md
- specialities/platform-windows/theming.md
- specialities/platform-windows/windows-architecture.md

## Exploratory Prompts

1. Why does Fluent Design emphasize simplicity and focus? What assumptions about desktop apps is that challenging?

2. What if you had to support every DPI from 96 to 500 without custom pixel fiddling? How would you think about scaling?

3. If nullable reference types are enabled, what does that tell you about the code's intent?

4. Why is "use TextFillColorPrimary" better than "use #FFFFFF"? What's the relationship between semantic colors and maintainability?
