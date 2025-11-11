# Teodor Đurić

**Backend Software Engineer** | Building systems in Go & Rust

Currently seeking backend engineering opportunities primarily in Go, Rust, or Python. Open to remote work worldwide.

🔭 Building distributed systems and developer tooling  
🌱 Exploring async Rust, concurrency patterns, and systems programming  
⚡ Recent: Built [csc.nvim](https://github.com/yus-works/csc.nvim) - 35⭐, featured in [awesome-neovim](https://github.com/rockerBOO/awesome-neovim)

📫 **Contact:**
- **Email:** [teodor@yus.rs](mailto:teodor@yus.rs)
- **LinkedIn:** [linkedin.com/in/teodord25](https://linkedin.com/in/teodord25)
- **Portfolio:** [yus.rs](https://yus.rs)
- **Projects:** [@yus-works](https://github.com/yus-works) (my project organization)

---

## 🚀 Featured Projects

### [Job Watcher](https://github.com/yus-works/job-watcher) | Go Backend Service
> Production-ready job aggregator processing 500+ listings daily from 6+ concurrent sources

**What it does:** Aggregates remote software engineering jobs from multiple APIs and RSS feeds into a unified interface with real-time updates, deduplication, and filtering.

**Technical highlights:**
- **Data pipeline**: Concurrent feed fetching of 6+ sources using goroutines and WaitGroups
- **Efficient deduplication**: Content-based hashing reduces duplicate writes
- **Real-time streaming**: Server-Sent Events with HTMX for live job updates without polling
- **Performance monitoring**: Custom httptrace integration tracks DNS, TLS, and TTFB metrics for each source
- **Production deployment**: Multi-stage Docker build, deployed on Fly.io with SQLite persistence

**Stack:** Go 1.21, SQLite, HTMX, Logrus, Docker, Fly.io  
**Architecture:** Feed parsers -> Concurrent fetcher -> Normalizer -> Deduplicator -> SQLite -> SSE stream -> HTMX UI

---

### [csc.nvim](https://github.com/yus-works/csc.nvim) | Neovim Plugin (35⭐)
> Intelligent conventional commit scope suggestions learned from your repository's history

**What it does:** Analyzes your Git history to provide smart autocomplete for commit scopes, ensuring consistency without config files.

**Why it matters:**
- **Featured in awesome-neovim**: Curated list of quality Neovim plugins
- **Community validation**: Saghen (creator of blink.cmp) personally contributed to add blink.cmp support
- **Pure Lua implementation**: No Node.js dependencies, lives entirely in your editor
- **Real user adoption**: 35 stars, community contributions, used in production workflows

**Technical highlights:**
- Async git operations using `jobstart` for non-blocking performance
- Custom nvim-cmp and blink.cmp source implementations
- Frequency-based ranking algorithm for scope suggestions
- Smart caching with configurable TTL (30s default)

**Stack:** Lua, Neovim API, Git, nvim-cmp, blink.cmp

**Learning:** Built this to solve my own workflow problem. Learned how to design Neovim plugins, work with completion engines, and collaborate with OSS communities. The experience of getting it accepted into awesome-neovim taught me how OSS projects gain traction through ecosystem integration. When Saghen contributed blink.cmp integration, it taught me how quality projects attract contributions from ecosystem creators. Getting featured in awesome-neovim showed me that ecosystem integration matters more than direct marketing.

---

### [Mycelia](https://github.com/yus-works/mycelia) | Rust Concurrent Crawler (WIP)

Async Wikipedia crawler exploring concurrent programming patterns in Rust

What it does: Crawls Wikipedia pages, extracts links, builds graph structures, and visualizes relationships using D3.js.
Technical highlights:

Async/await patterns: Built with Tokio for efficient concurrent HTTP requests
WebSocket real-time updates: Actix-web WebSocket integration for live crawler status
Concurrent coordination: Tokio tasks, channels, and async primitives for efficient I/O-bound workloads

Stack: Rust, Tokio, Actix-web, SQLx, PostgreSQL, WebSocket, D3.js
Status: Active development - working through async Rust concurrency patterns and graph traversal algorithms

---

### [yus.rs](https://github.com/yus-works/yus) | Personal Portfolio
> Portfolio site with WebGPU shader demonstrations

**Technical highlights:**
- Built with Leptos (Rust web framework)
- WebGPU shader examples demonstrating graphics programming
- Server-side rendering with Rust

**Stack:** Rust, Leptos, WebGPU, WGSL shaders

---

## 🤝 Open to Opportunities

I'm open to **backend engineering roles** where I can work with:
- **Go** or **Rust** backend systems
- Concurrent/parallel processing
- Distributed systems
- API design and implementation
- Database optimization

**What I bring:**
- Strong fundamentals in concurrent programming and systems design
- Track record of shipping production code and open-source contributions
- Self-directed learning and problem-solving
- Ability to work across the stack when needed

**Location:** Senta, Serbia | **Remote:** Worldwide | **Relocation:** Open to discussion


💡 **Open to:** Full-time roles, contract work, interesting open-source collaboration

---

⭐ If you find my projects interesting, consider starring them or reaching out!
