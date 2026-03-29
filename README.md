<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="MiroFish Logo" width="75%"/>

<a href="https://trendshift.io/repositories/16144" target="_blank"><img src="https://trendshift.io/api/badge/repositories/16144" alt="666ghj%2FMiroFish | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

A simple, universal swarm intelligence engine for predicting anything
</br>
<em>A Simple and Universal Swarm Intelligence Engine, Predicting Anything</em>

<a href="https://www.shanda.com/" target="_blank"><img src="./static/image/shanda_logo.png" alt="666ghj%2MiroFish | Shanda" height="40"/></a>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/MiroFish?style=flat-square&color=DAA520)](https://github.com/666ghj/MiroFish/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/666ghj/MiroFish)

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white)](http://discord.gg/ePf5aPaHnA)
[![X](https://img.shields.io/badge/X-Follow-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/mirofish_ai)
[![Instagram](https://img.shields.io/badge/Instagram-Follow-E4405F?style=flat-square&logo=instagram&logoColor=white)](https://www.instagram.com/mirofish_ai/)

[README](./README.md) | [English Copy](./README-EN.md)

</div>

## ⚡ Overview

**MiroFish** is a next-generation AI prediction engine powered by multi-agent technology. By extracting seed information from the real world (such as breaking news, policy drafts, or financial signals), it automatically constructs a high-fidelity parallel digital world. Within this space, thousands of intelligent agents with independent personalities, long-term memory, and behavioral logic freely interact and undergo social evolution. You can inject variables dynamically from a "God's-eye view" to precisely deduce future trajectories — **rehearse the future in a digital sandbox, and win decisions after countless simulations**.

> You only need to: upload seed materials (data analysis reports or interesting novel stories) and describe your prediction requirements in natural language</br>
> MiroFish will return: a detailed prediction report and a deeply interactive high-fidelity digital world

### Our Vision

MiroFish is dedicated to creating a swarm intelligence mirror that maps reality. By capturing the collective emergence triggered by individual interactions, we break through the limitations of traditional prediction:

- **At the Macro Level**: We are a rehearsal laboratory for decision-makers, allowing policies and public relations to be tested at zero risk
- **At the Micro Level**: We are a creative sandbox for individual users, whether deducing novel endings or exploring imaginative scenarios, everything can be fun, playful, and accessible

From serious predictions to playful simulations, we let every "what if" see its outcome, making it possible to predict anything.

## 🌐 Live Demo

Visit our online demo environment and experience a prediction simulation around a trending public-opinion event: [mirofish-live-demo](https://666ghj.github.io/mirofish-demo/)

## 📸 Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/screenshot-1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/screenshot-2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/screenshot-3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/screenshot-4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/screenshot-5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/screenshot-6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

## 🎬 Demo Videos

### 1. Wuhan University Public Opinion Simulation + MiroFish Project Introduction

<div align="center">
<a href="https://www.bilibili.com/video/BV1VYBsBHEMY/" target="_blank"><img src="./static/image/wuhan-demo-cover.png" alt="MiroFish Demo Video" width="75%"/></a>

Click the image to watch the complete demo video for prediction using the BettaFish-generated "Wuhan University Public Opinion Report."
</div>

### 2. Dream of the Red Chamber Lost Ending Simulation

<div align="center">
<a href="https://www.bilibili.com/video/BV1cPk3BBExq" target="_blank"><img src="./static/image/dream-of-red-chamber-cover.jpg" alt="MiroFish Demo Video" width="75%"/></a>

Click the image to watch MiroFish predict the lost ending based on the first 80 chapters of *Dream of the Red Chamber*.
</div>

> **Financial prediction**, **current-events forecasting**, and more examples are coming soon.

## 🔄 Workflow

1. **Graph Building**: Seed extraction, individual and collective memory injection, and GraphRAG construction
2. **Environment Setup**: Entity relationship extraction, persona generation, and agent configuration injection
3. **Simulation**: Dual-platform parallel simulation, automatic prediction-requirement parsing, and dynamic temporal memory updates
4. **Report Generation**: ReportAgent uses a rich toolset to interact deeply with the post-simulation environment
5. **Deep Interaction**: Chat with any agent in the simulated world and continue the conversation with ReportAgent

## 🚀 Quick Start

### Option 1: Source Deployment (Recommended)

#### Prerequisites

| Tool | Version | Description | Check Installation |
|------|---------|-------------|-------------------|
| **Node.js** | 18+ | Frontend runtime, includes npm | `node -v` |
| **Python** | ≥3.11, ≤3.12 | Backend runtime | `python --version` |
| **uv** | Latest | Python package manager | `uv --version` |

#### 1. Configure Environment Variables

```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file and fill in the required API keys
```

**Required Environment Variables:**

```env
# LLM API configuration (supports any LLM API compatible with the OpenAI SDK format)
# Recommended: use the qwen-plus model on Alibaba Bailian: https://bailian.console.aliyun.com/
# Note: usage can be expensive, so try simulations with fewer than 40 rounds first
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Graph backend selection
# Use zep_cloud for hosted Zep, or graphiti_local for local Neo4j + Graphiti
GRAPH_BACKEND=zep_cloud

# Zep Cloud configuration
# Required only when GRAPH_BACKEND=zep_cloud
ZEP_API_KEY=your_zep_api_key

# Local Graphiti + Neo4j configuration
# Required only when GRAPH_BACKEND=graphiti_local
# Note: the local Graphiti backend stores all graphs in one Neo4j database
# and isolates each MiroFish graph by Graphiti `group_id`.
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

#### 2. Install Dependencies

```bash
# One-click installation of all dependencies (root + frontend + backend)
npm run setup:all
```

Or install them step by step:

```bash
# Install Node dependencies (root + frontend)
npm run setup

# Install Python dependencies (backend, auto-creates virtual environment)
npm run setup:backend
```

#### 3. Start Services

```bash
# Start both frontend and backend (run from the project root)
npm run dev
```

If you use `GRAPH_BACKEND=graphiti_local`, start Neo4j too:

```bash
docker compose up -d neo4j
```

The bundled `docker-compose.yml` uses `neo4j:5.26.22-enterprise` with
`NEO4J_ACCEPT_LICENSE_AGREEMENT=yes` as the safe default for local compatibility.
The current local backend still keeps all graphs in the default Neo4j database
and maps each MiroFish `graph_id` directly to a Graphiti `group_id`.

**Service URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Start Individually:**

```bash
npm run backend   # Start the backend only
npm run frontend  # Start the frontend only
```

### Option 2: Docker Deployment

```bash
# 1. Configure environment variables (same as source deployment)
cp .env.example .env

# 2. Pull the image and start
docker compose up -d
```

Docker reads `.env` from the project root by default and maps ports `3000 (frontend) / 5001 (backend)`.

> A mirror image URL is provided as a comment in `docker-compose.yml` if you need a faster pull source.
> When `GRAPH_BACKEND=graphiti_local`, the bundled compose stack starts a local Neo4j instance for Graphiti storage. The repo keeps the enterprise image as the default compose target because existing local stores may use the block format.

## 📬 Join the Conversation

<div align="center">
<img src="./static/image/qq-group.png" alt="QQ Group" width="60%"/>
</div>

&nbsp;

The MiroFish team is recruiting for full-time and internship roles. If you are interested in multi-agent simulation and LLM applications, send your resume to: **mirofish@shanda.com**

## 📄 Acknowledgments

**MiroFish has received strategic support and incubation from Shanda Group.**

MiroFish's simulation engine is powered by **[OASIS](https://github.com/camel-ai/oasis)**, and we sincerely thank the CAMEL-AI team for their open-source contributions.

## 📈 Project Statistics

<a href="https://www.star-history.com/#666ghj/MiroFish&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
 </picture>
</a>
