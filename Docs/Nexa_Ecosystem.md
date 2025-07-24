# NexaPod Economic Ecosystem

NexaPod Economic Ecosystem is a scalable, permissionless, compute-driven economy for scientific advancement.

## 1. Overview

The NexaPod ecosystem is a decentralized compute mesh designed to solve massive-scale scientific problems. It leverages a flexible, modular economic model centered on NexaCredits, compute tiers, and incentivized contribution pools.

## 2. Compute Pools

There are four primary compute pools:

1. **Hot Pool (Active Compute)**
   - Runs the current compute job (e.g., DreamMS + Atlas++).
   - Participants receive maximum rewards.
   - High-throughput tasks such as model training or inference run here.
   - Nodes must pass cryptographic verification (hashes, hardware fingerprint).
   - Contributions are tracked in real time and signed.

2. **Warm Pool (Post-Job or Idle Compute)**
   - Compute remains registered and visible in the Nexa Marketplace.
   - Contributors can lease idle capacity in exchange for:
     - NexaCredits
     - Stablecoins (USDC)
     - Fiat (via integrated APIs)
   - Offers persistent compute services between major jobs.

3. **Cold Pool (Redundant / Standby)**
   - It Comprises approximately 10–20% of the Hot Pool capacity.
   - Receives baseline incentives:
     - 5–10 USDC
     - 5 NexaCredits per week
   - Used for failover and node substitution.
   - Keeps jobs running seamlessly in case of disruptions.

4. **Institutional Pool**
   - Designed for contributors offering >1 ExaFLOP or institutional compute clusters.
   - No direct monetary or credit rewards.
   - Offers free unlimited access to Atlas++ and exclusive early research privileges.
   - Caters to particularly large or complex tasks that require elite hardware.

## 3. Compute Measurement and Reward

- **Compute Caps:**  
  - Individual (Hacker-tier) nodes are capped at 500 TFLOPs to 1 ExaFLOP.
  - No single user may control more than 30–40% of the total Hot Pool capacity to prevent centralization.

- **Reward Rates (Hot Pool):**  
  - 1,000 FLOPs = 1 NexaCredit  
  - 2,000 FLOPs = 0.1 USDC  
  - Rewards scale logarithmically up to the cap.
  - Contributions are logged in a signed, tamper-proof ledger.

- **Reward Rates (Cold Pool):**  
  - Flat reward of 5 NexaCredits and 5–10 USDC per week.
  - Upgraded to Hot Pool rewards if disruptions occur.

## 4. Contributor Registry

Each verified contributor receives:
- Username
- Hardware profile
- Hash-signed identity verification
- Leaderboard status (based on cumulative compute)
- NexaCredit balance
- Option to remain in the Warm Pool for ongoing compute resale

## 5. NexaCredits: Internal Economy

**Usage:**
- Redeemable for:
  - Access to datasets, APIs, and foundational models
  - Subscriptions to Nexa tools (e.g. NexaPrompt, NexaCodex)
  - Membership tiers, consulting, and software licenses
  - GitHub sponsorships or HF-hosted perks

**Exchange:**
- NexaCredits can be:
  - Sold on the Nexa Marketplace for stablecoins (USDC) or fiat
  - Traded peer-to-peer among contributors
  - Pooled into institutional credit accounts

## 6. Verification & Integrity

Every node must:
- Pass hash verification (using signed runner code)
- Share a hardware profile
- Operate within an isolated container (e.g. Kubernetes pod)
- Suffer a blacklist status if tampering is detected

All jobs are checkpointed and fault-tolerant, with compute cycles cryptographically signed for traceability.

## 7. Compute Lifecycle & Voting

Each cycle (approximately 3–4 weeks) includes:
- **Weeks 1–2:** Compute phase
- **Weeks 2–3:** Paper writing, repository packaging, and verification
- **Week 4:** Public release and community voting
  - NexaLabs proposes 4 potential scientific targets
  - Contributors vote via GitHub or the Nexa dashboard

## 8. Atlas++ Access Model

- **Free Access:** For contributors and verified institutions.
- **Paid Access:** For general users, API-based clients, and external companies.

## Summary

The NexaPod economic ecosystem establishes a permissionless, self-sustaining infrastructure for advancing frontier science. By aligning incentives around compute contribution, scientific rigor, and transparency, NexaPod transforms idle hardware into breakthroughs—rewarding every contributor along the way.

*Your GPU can change the world. Welcome to Nexa.*
