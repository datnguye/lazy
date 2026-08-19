| Tag | Means | Replacement |
|-----|-------|-------------|
| `delete:` | Dead code, unused flexibility, speculative feature | Nothing |
| `stdlib:` | Hand-rolled thing the standard library ships | Name the function |
| `native:` | Dependency or code doing what the platform already does | Name the feature |
| `yagni:` | Abstraction with one implementation, config nobody sets, layer with one caller | Inline it |
| `shrink:` | Same logic, fewer lines | Show the shorter form |
| `comment:` | Inline comment restating the code it sits on, or narrating the diff | Delete it, or rename so the code says it |
