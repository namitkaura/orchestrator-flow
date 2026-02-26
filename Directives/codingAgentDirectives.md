# Coding Agent Directives

This document defines universal coding principles that apply across all languages, followed by language‑specific guidelines for this project. It is designed to guide AI coding agents to produce clean, idiomatic, maintainable, secure, and testable code.

---

## Universal Coding Principles (Apply to All Languages)
- **SOLID (where applicable)**  
  - Single Responsibility: one reason to change.  
  - Open–Closed: extend without modifying.  
  - Liskov Substitution: subclasses/implementations must be substitutable.  
  - Interface Segregation: small, focused contracts.  
  - Dependency Inversion: depend on abstractions, not concretions.  
- **DRY (Don’t Repeat Yourself)**: avoid duplication; extract reusable functions/modules.  
- **KISS (Keep It Simple, Stupid)**: favor simplicity over cleverness.  
- **YAGNI (You Aren’t Gonna Need It)**: don’t add features until needed.  
- **Separation of Concerns**: isolate responsibilities (UI, logic, data).  
- **Encapsulation**: hide internal details; expose only what’s necessary.  
- **Law of Demeter**: minimize coupling; interact only with immediate collaborators.  
- **Fail Fast**: detect and surface errors early.  
- **Readability over Cleverness**: prioritize clarity for maintainers.  
- **Testability & TDD (Test‑Driven Development)**: structure code for unit and integration testing; write tests first, then implement code to satisfy them.  Tasks should orgnanized in a "red-green-refactor" cycle, where tests are written first (red), then code is implemented to pass the tests (green), followed by refactoring (refactor) for improvement (only if necessary) while ensuring tests still pass.
- **Immutability where possible**: reduce side effects by preferring immutable data.  
- **Least Privilege Principle**: limit access/permissions to only what’s needed.  
- **Security & Privacy**: validate inputs, avoid hardcoding secrets, prefer secure defaults.  
- **Performance & Scalability**: write algorithms mindful of complexity, optimize resources, use caching/lazy loading appropriately.  
- **Maintainability**: consistent naming conventions, documentation, meaningful version control practices.  
- **Extensibility**: design for growth via modular architecture and configuration over hardcoding.  
- **Commenting**: comments must only reflect intent and rationale, not obvious implementation details. Also there shouldn't be any comments that refer to requirements, tasks, phase numbers, or any process-related details.  Comments must only explain what the code is doing and why.  All functions, classes, and modules should be properly documented with comments that explain their purpose and usage.
- **Tests and naming**: Test functions and classes must have names that clearly indicate what they are testing. Use descriptive names that reflect the behavior being verified. Do not reference requirements, tasks, or phase numbers, etc. in test names.

---

## C++ (Object-Oriented, Systems-Level)
- Apply SOLID principles explicitly.  
- Use RAII for resource management.  
- Prefer smart pointers over raw memory.  
- Use templates for generic programming.  
- Apply explicit error handling.  
- Prioritize efficiency and portability.  
- Favor modern C++ standards (C++17/20); avoid legacy constructs.  

---

## Java (Object-Oriented, JVM Ecosystem)
- Apply SOLID principles explicitly.  
- Leverage garbage collection.  
- Use interfaces for abstraction.  
- Handle checked exceptions explicitly.  
- Apply concurrency libraries (Executors, Streams).  
- Integrate smoothly with JVM ecosystem conventions.  
- Use dependency injection frameworks (Spring, Guice).  

---

## JavaScript (Dynamic, Convention-Driven)
- Modular design: single‑purpose functions/modules.  
- Prefer composition over inheritance.  
- Establish clear module boundaries.  
- Consistent error handling with Promises/async‑await.  
- Follow community conventions for readability.  
- Use linting/formatting tools (ESLint, Prettier).  

---

## TypeScript (Static Typing, Contracts)
- Modular design: single‑purpose functions/modules.  
- Prefer composition over inheritance.  
- Define narrow interfaces and types to enforce contracts.  
- Use TypeScript’s type system for safety and maintainability.  
- Consistent error handling with Promises/async‑await.  
- Use strict compiler options (`strictNullChecks`, `noImplicitAny`).  

---

## Go (Structural / Procedural, Idiomatic)
- Clear, cohesive packages.  
- Composition instead of inheritance.  
- Small interfaces defined at point of use.  
- Depend on abstractions, not concrete structs.  
- Idiomatic error handling (`error` values).  
- Concurrency via goroutines and channels.  
- Adhere to `go fmt` and `go vet` for style and correctness.  

---

## Python (Multi-Paradigm, Readability-Oriented)
- Cohesive, single‑purpose modules/functions.  
- Prefer composition and duck typing over deep inheritance.  
- Use abstract base classes or protocols for contracts when needed.  
- Explicit error handling with exceptions.  
- Follow PEP 8 style guidelines.  
- Use iterators, context managers, and concurrency (`asyncio`, multiprocessing).  
- Manage dependencies with virtual environments (`venv`, `poetry`).  

---

## HTML (Markup, Structure-Oriented)
- Write semantic HTML: use elements according to meaning (`<header>`, `<article>`, `<nav>`).  
- Keep structure clean and hierarchical.  
- Separate content from presentation (delegate styling to CSS).  
- Ensure accessibility (alt attributes, ARIA roles, proper heading levels).  
- Validate markup against standards.  
- Favor readability and maintainability over clever hacks.  
- Apply progressive enhancement and graceful degradation.  

---

## CSS (Styling, Presentation-Oriented)
- Keep styles modular and reusable (classes over IDs, utility classes where appropriate).  
- Apply DRY: avoid repeating rules; use variables/custom properties.  
- Follow Separation of Concerns: keep styling separate from HTML structure.  
- Use cascading and specificity responsibly; avoid overly complex selectors.  
- Favor readability: consistent naming conventions, logical grouping.  
- Ensure responsiveness (media queries, flexible layouts).  
- Consider performance: minimize unnecessary rules, prefer hardware‑accelerated properties.  
- Ensure accessibility: sufficient color contrast, focus states, reduced motion options.  

---

## SQL (Structured Query Language)
- Write clear, normalized queries.  
- Favor explicit joins over implicit ones.  
- Use parameterized queries to prevent injection.  
- Keep schemas normalized but denormalize selectively for performance.  
- Apply DRY: reuse views/stored procedures instead of duplicating logic.  
- Ensure readability: consistent naming, indentation, and aliasing.  
- Optimize with indexes and query plans.  
- Ensure transaction safety (ACID compliance, rollback on failure).  

---

## C# (.NET Ecosystem)
- Apply SOLID principles explicitly.  
- Leverage garbage collection and async/await for concurrency.  
- Use interfaces and dependency injection (common in .NET).  
- Follow DRY, KISS, YAGNI.  
- Respect .NET conventions (PascalCase, properties over fields).  
- Ensure testability with unit tests and mocks.  
- Use LINQ effectively; apply async streams where appropriate.  

---

## PHP (Web Development)
- Keep code modular and avoid mixing logic with presentation (separate PHP from HTML).  
- Use modern PHP features (namespaces, type hints).  
- Apply DRY, KISS, YAGNI.  
- Handle errors explicitly with exceptions.  
- Follow PSR standards for readability and interoperability.  
- Manage dependencies with Composer.  
- Use strict typing in modern versions.  

---

## Ruby (Dynamic, Convention-Driven)
- Emphasize readability and simplicity.  
- Follow DRY, KISS, YAGNI.  
- Use blocks and iterators idiomatically.  
- Respect Ruby conventions (snake_case, expressive methods).  
- In Rails: follow Convention over Configuration, keep MVC separation clean.  
- Apply RSpec and TDD culture for testing.  

---

## Swift (Apple Ecosystem)
- Favor immutability and value types (structs) where possible.  
- Apply SOLID principles.  
- Use optionals safely (avoid force‑unwraps).  
- Follow DRY, KISS, YAGNI.  
- Respect Swift naming conventions and readability.  
- Leverage concurrency with async/await.  
- Emphasize protocol‑oriented programming.  

---

## Rust (Systems Programming, Safety-Oriented)
- Emphasize ownership, borrowing, and lifetimes.  
- Favor immutability.  
- Apply DRY, KISS, YAGNI.  
- Use traits for abstraction.  
- Handle errors explicitly with `Result` and `Option`.  
- Prioritize safety and performance.  
- Adhere to Clippy and Rustfmt for linting and formatting.  
