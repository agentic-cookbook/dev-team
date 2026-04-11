---
name: dependency-clusters
description: Analyzes import graphs to find clusters with high internal coupling and low external coupling as natural scope group candidates.
artifact: guidelines/codebase-decomposition/dependency-clusters.md
version: 1.0.0
---

## Worker Focus
Build and analyze the import graph. Compute internal vs external coupling ratios per cluster. Clusters with high internal coupling and low external coupling are natural scope group candidates.

## Verify
Import graph analyzed; coupling ratios computed per cluster; high-coupling clusters identified as candidate scope groups.
