# envsnap

> CLI tool to snapshot and restore local environment variables across projects

---

## Installation

```bash
pip install envsnap
```

---

## Usage

**Save a snapshot of your current environment:**

```bash
envsnap save myproject
```

**Restore a saved snapshot:**

```bash
envsnap restore myproject
```

**List all saved snapshots:**

```bash
envsnap list
```

**Delete a snapshot:**

```bash
envsnap delete myproject
```

Snapshots are stored locally in `~/.envsnap/` as encrypted files, keeping your environment variables safe and organized across projects.

---

## Example Workflow

```bash
# Working on project A — save its environment
envsnap save project-a

# Switch to project B and load its environment
envsnap restore project-b

# Verify active environment variables
envsnap show project-b
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)