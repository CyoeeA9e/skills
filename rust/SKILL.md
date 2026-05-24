---
name: rust
description: Use when working with Rust code, Cargo projects, or when implementing features in Rust
---

# Rust

## Overview

Rust is a systems programming language focused on safety, speed, and concurrency without a garbage collector. The compiler (`rustc`) and build system (`cargo`) enforce memory safety at compile time.

## Project Structure

```
my-project/
  Cargo.toml          # Manifest: dependencies, metadata, workspace config
  Cargo.lock          # Lockfile (commit to version control for binaries)
  src/
    main.rs           # Binary entry point (or lib.rs for libraries)
    lib.rs            # Library root
    bin/              # Additional binaries
  tests/              # Integration tests
  examples/           # Example binaries
  benches/            # Benchmarks (nightly or criterion)
```

**Workspace conventions:**
```toml
# Root Cargo.toml
[workspace]
members = ["crates/*", "app"]
resolver = "2"
```

## Key Commands

| Command | Purpose |
|---------|---------|
| `cargo check` | Fast compile check (no codegen) - use during development |
| `cargo build` | Build debug |
| `cargo build --release` | Build release |
| `cargo test` | Run all tests |
| `cargo test name` | Run tests matching name |
| `cargo test -- --nocapture` | Show stdout/stderr |
| `cargo clippy` | Lint (fix: `cargo clippy --fix`) |
| `cargo fmt` | Format code |
| `cargo doc --open` | Build and open docs |
| `cargo add crate` | Add dependency |
| `cargo remove crate` | Remove dependency |
| `cargo upgrade` | Update dependencies (need `cargo-edit`) |

## Testing

### Unit Tests (in `src/`)

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    fn test_error_case() {
        let result = parse("invalid");
        assert!(result.is_err());
    }
}
```

### Integration Tests (in `tests/`)

```rust
use my_crate;

#[test]
fn integration_test() {
    let result = my_crate::do_thing();
    assert!(result.is_ok());
}
```

### Doc Tests

```rust
/// Adds two numbers
///
/// ```
/// use my_crate::add;
/// assert_eq!(add(2, 2), 4);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

## Error Handling

### Library code: use `thiserror`

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("network error: {0}")]
    Network(#[from] reqwest::Error),
    #[error("invalid input: {msg}")]
    InvalidInput { msg: String },
}
```

### Application code: use `anyhow`

```rust
use anyhow::{Result, Context};

fn do_thing() -> Result<()> {
    let data = read_file("path")
        .context("failed to read config")?;
    Ok(())
}
```

### Pattern: `Result<T, E>` with `?`

```rust
fn process() -> Result<Data, Error> {
    let input = fetch_input()?;  // early return on error
    let parsed = parse(input)?;
    Ok(parsed)
}
```

## Common Patterns

### Builder Pattern

```rust
#[derive(Default)]
pub struct ConfigBuilder {
    timeout: Option<Duration>,
    retries: Option<u32>,
}

impl ConfigBuilder {
    pub fn timeout(mut self, d: Duration) -> Self {
        self.timeout = Some(d);
        self
    }
    pub fn retries(mut self, n: u32) -> Self {
        self.retries = Some(n);
        self
    }
    pub fn build(self) -> Result<Config, ConfigError> {
        Ok(Config {
            timeout: self.timeout.unwrap_or(Duration::from_secs(30)),
            retries: self.retries.unwrap_or(3),
        })
    }
}
```

### Newtype Pattern

```rust
#[derive(Debug, Clone)]
pub struct Email(String);

impl Email {
    pub fn new(s: String) -> Result<Self, String> {
        if s.contains('@') {
            Ok(Self(s))
        } else {
            Err("invalid email".into())
        }
    }
}
```

### Iterator Chains

```rust
let result: Vec<_> = items
    .iter()
    .filter(|x| x.is_valid())
    .map(|x| x.transform())
    .collect();
```

## Async

Use `tokio` for async runtime:

```rust
#[tokio::main]
async fn main() -> Result<()> {
    let data = fetch_data().await?;
    Ok(())
}

async fn fetch_data() -> Result<Data> {
    let resp = reqwest::get("https://api.example.com")
        .await?
        .json::<Data>()
        .await?;
    Ok(resp)
}
```

## Common Crates

| Category | Crate | Notes |
|----------|-------|-------|
| Async runtime | `tokio` | Default async runtime |
| HTTP client | `reqwest` | Async HTTP client |
| Serialization | `serde` + `serde_json` | JSON (also `serde_yaml`, `serde_xml`) |
| Errors (lib) | `thiserror` | Derive macro for error types |
| Errors (app) | `anyhow` | Ergonomic error handling |
| Logging | `tracing` | Structured logging (use `log` crate for simple cases) |
| CLI | `clap` | Argument parsing (derive API) |
| Config | `config` | Multi-source config |
| Date/Time | `chrono` | Date and time types |
| Random | `rand` | Random number generation |
| UUID | `uuid` | UUID generation |
| Pattern matching | `itertools` | Extra iterator adaptors |

## Cargo.toml Best Practices

```toml
[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"
rust-version = "1.75"  # MSRV

[dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
tempfile = "3"
pretty_assertions = "1"

[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1
```

## Code Style

### Code Organization

Never using `mod.rs`.

```
// Good
|- server.rs
|- server
|--- http.rs

// Bad
|- server
|--- mod.rs
|--- http.rs
```



### Early Return

Prefer returning early from functions rather than deep nesting with `else`:

```rust
// Good
fn process(data: &[u8]) -> Result<Output> {
    if data.is_empty() {
        return Err("empty data".into());
    }
    if data.len() < HEADER_SIZE {
        return Err("data too short".into());
    }
    // main logic here, no else needed
    parse_body(data)
}

// Bad
fn process(data: &[u8]) -> Result<Output> {
    if data.is_empty() {
        Err("empty data".into())
    } else if data.len() < HEADER_SIZE {
        Err("data too short".into())
    } else {
        parse_body(data)
    }
}
```

### Prefer `match` over `if else if else`

Use `match` for any branching with 2+ conditions:

```rust
// Good
match status {
    Status::Active => handle_active(),
    Status::Pending => handle_pending(),
    Status::Banned => handle_banned(),
}

// Bad
if status == Status::Active {
    handle_active()
} else if status == Status::Pending {
    handle_pending()
} else {
    handle_banned()
}
```

Use `if let` only for single-pattern matches:

```rust
// Good (single pattern, don't care about others)
if let Some(value) = optional {
    process(value);
}

// Bad (multiple arms → use match)
if let Some(x) = opt {
    a(x)
} else {
    b()
}
// Use match instead:
match opt {
    Some(x) => a(x),
    None => b(),
}
```

### Prefer References over Clone

```rust
// Good
fn process(data: &[u8]) {
    // use data as reference
}

// Bad
fn process(data: Vec<u8>) {
    // forces caller to clone
}

// Good - accept reference, clone only when needed internally
fn transform(data: &[u8]) -> Vec<u8> {
    data.iter().map(|b| b + 1).collect()
}

// Bad - clone at call site
let transformed = transform(data.clone());
```

### Prefer Chained Calls over Imperative Control Flow

Use `Option`/`Result` combinators (`and_then`, `map`, `map_err`, `or_else`, `ok_or_else`) instead of manual `match` or `if`.

```rust
// Good
fn parse_user(data: &[u8]) -> Result<User> {
    parse_header(data)
        .and_then(|h| validate_version(h))
        .and_then(|h| parse_body(data, h))
        .map_err(|e| Error::Parse(e.to_string()))
}

// Bad
fn parse_user(data: &[u8]) -> Result<User> {
    let header = parse_header(data)?;
    let version = validate_version(header)?;
    let body = parse_body(data, header)?;
    Ok(body)
}
```

### Functional Style Preferred

Prefer iterator combinators over imperative loops:

```rust
// Good
let active_names: Vec<_> = users
    .iter()
    .filter(|u| u.is_active)
    .map(|u| u.name.as_str())
    .collect();

// Bad
let mut active_names = Vec::new();
for user in &users {
    if user.is_active {
        active_names.push(user.name.clone());
    }
}

// Good - use Option combinators
fn find_owner(item: &Item) -> Option<&User> {
    item.owner_id
        .and_then(|id| users.get(id))
        .or(Some(&default_user))
}

// Bad - manual match
fn find_owner(item: &Item) -> Option<&User> {
    match item.owner_id {
        Some(id) => match users.get(id) {
            Some(user) => Some(user),
            None => Some(&default_user),
        },
        None => Some(&default_user),
    }
}
```

### Prefer Builder Pattern for Construction

Use `ConfigBuilder`-style patterns for structs with optional fields:

```rust
// Good
let config = Config::builder()
    .timeout(Duration::from_secs(60))
    .retries(5)
    .build()?;

// Bad - positional args, many params
let config = Config::new(
    Duration::from_secs(60),
    5,
    None,
    None,
    Some(true),
)?;
```

## Code Organization

- One module per file, declared in `lib.rs` or `mod.rs`
- `pub use` to re-export public API
- Keep modules focused and small
- Put types near where they're used

```rust
// lib.rs
pub mod config;
pub mod error;
pub mod types;
pub mod utils;

pub use config::Config;
pub use error::AppError;
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `clone()` everywhere | Pass references, restructure ownership |
| Blocking in async context | Use `tokio::fs` instead of `std::fs`, `spawn_blocking` for CPU work |
| `unwrap()`/`expect()` in library code | Return `Result` instead |
| Overly generic lifetimes | Let lifetime elision work by default |
| `mut` on everything | Prefer immutable by default, use interior mutability patterns when needed |
| Missing `?Sized` on trait objects | Add `?Sized` bound or use `Box<dyn Trait>` |
