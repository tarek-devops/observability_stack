# What is the Vanilla Approach?

> **Vanilla Kubernetes** (or vanilla deployments) means running the core open-source Kubernetes project as-is, with minimal or no vendor-specific customization.

---

## Key Characteristics

- **Write your own YAML manifests**: You define Deployments, Services, Ingresses, ConfigMaps, etc.
- **Manual management**: You handle upgrades, scaling, and monitoring yourself.
- **No vendor-specific extensions/operators**: Pure upstream Kubernetes, no managed add-ons or CRDs from vendors.

---

## Pros

- Maximum flexibility and control
- No vendor lock-in
- Great for learning and experimentation

---

## Cons

- Steeper learning curve
- More manual work for lifecycle management
- Harder to maintain at scale