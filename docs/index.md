---
layout: default
title: Home
nav_order: 1
---

<section class="home-hero">
  <div class="home-hero-text">
    <p class="home-eyebrow">Hands-on workshop</p>
    <h1>Dynatrace AI Observability Workshop</h1>
    <p class="home-lead">Learn to monitor AI and LLM applications with Dynatrace and the Model Context Protocol (MCP): from instrumentation to automated cost alerts.</p>
    <div class="hero-buttons">
      <a href="https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1" class="btn btn-light" target="_blank" rel="noopener">Launch workshop environment</a>
      <a href="lab0-setup" class="btn btn-outline-light">Start Lab 0</a>
    </div>
  </div>
  <img class="home-hero-badge" src="{{ '/assets/images/badge.svg' | relative_url }}" alt="">
</section>

<div class="home-stats">
  <div class="home-stat"><span class="home-stat-value">1.5 – 2 h</span><span class="home-stat-label">Duration</span></div>
  <div class="home-stat"><span class="home-stat-value">Intermediate</span><span class="home-stat-label">Level</span></div>
  <div class="home-stat"><span class="home-stat-value">5 labs</span><span class="home-stat-label">Hands-on modules</span></div>
  <div class="home-stat"><span class="home-stat-value">GitHub account</span><span class="home-stat-label">Plus basic Python</span></div>
</div>

## What you'll learn

<div class="home-grid">
  <div class="home-tile">
    <svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
    <h3>Instrument AI applications</h3>
    <p>Add OpenLLMetry and Traceloop to a Python AI app.</p>
  </div>
  <div class="home-tile">
    <svg viewBox="0 0 24 24" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
    <h3>Visualize LLM traces</h3>
    <p>Inspect prompts, completions, and token usage.</p>
  </div>
  <div class="home-tile">
    <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <h3>Analyze RAG pipelines</h3>
    <p>Debug retrieval and generation with distributed tracing.</p>
  </div>
  <div class="home-tile">
    <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/><line x1="8" y1="20" x2="16" y2="20"/><line x1="12" y1="16" x2="12" y2="20"/></svg>
    <h3>Use Dynatrace MCP</h3>
    <p>Query observability data directly from your IDE.</p>
  </div>
  <div class="home-tile">
    <svg viewBox="0 0 24 24" aria-hidden="true"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
    <h3>Automate workflows</h3>
    <p>Build AI cost alerts and daily summaries.</p>
  </div>
</div>

## Workshop agenda

<ol class="home-agenda">
  <li><span class="home-agenda-time">15 min</span><div><a href="lab0-setup">Lab 0: Environment setup</a><p>Configure your GitHub Codespace.</p></div></li>
  <li><span class="home-agenda-time">15 min</span><div><a href="lab1-instrumentation">Lab 1: AI instrumentation</a><p>Add OpenLLMetry to the sample app.</p></div></li>
  <li><span class="home-agenda-time">30 min</span><div><a href="lab2-explore-traces">Lab 2: Explore traces</a><p>Analyze AI traces in Dynatrace.</p></div></li>
  <li><span class="home-agenda-time">30 min</span><div><a href="lab3-dynatrace-mcp">Lab 3: Dynatrace MCP</a><p>Use MCP for agentic AI.</p></div></li>
  <li><span class="home-agenda-time">30 min</span><div><a href="lab4-automation">Lab 4: Workflow automation</a><p>Automate AI cost monitoring.</p></div></li>
</ol>

## What's included

<div class="home-grid home-grid-2">
  <div class="home-tile">
    <h3>Pre-configured Codespace</h3>
    <p>All dependencies installed and ready to run.</p>
  </div>
  <div class="home-tile">
    <h3>Sample RAG/LLM application</h3>
    <p>A working chatbot, ready for instrumentation.</p>
  </div>
  <div class="home-tile">
    <h3>Dynatrace playground</h3>
    <p>Access to a live environment for exploring your data.</p>
  </div>
  <div class="home-tile">
    <h3>Step-by-step lab guides</h3>
    <p>The pages you are reading now.</p>
  </div>
</div>

## Ready to begin?

<div class="home-cta">
  <a href="https://codespaces.new/marc-mas-ferrer/ai-mcp-ilt?quickstart=1" target="_blank" rel="noopener">
    <img src="https://github.com/codespaces/badge.svg" alt="Open in GitHub Codespaces" style="height: 44px;">
  </a>
</div>

> **Note:** Each attendee gets their own isolated Codespace environment. Your changes stay local to your Codespace and won't affect other attendees.

## Need help?

- Raise your hand during the workshop.
- Check the [Resources](resources) page for documentation links.
- Ask your workshop instructor.

<div class="lab-nav">
  <div></div>
  <a href="lab0-setup">Start Lab 0 →</a>
</div>
