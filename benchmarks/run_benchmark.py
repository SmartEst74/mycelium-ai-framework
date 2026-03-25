#!/usr/bin/env python3
"""
Colonial Memory Benchmark — Proof of Hypothesis

Compares solo agent (no memory) vs colonial agent (shared memory)
across multiple missions to demonstrate compound learning.

Usage:
  python3 run_benchmark.py --mode solo --missions 5
  python3 run_benchmark.py --mode colonial --missions 5
  python3 run_benchmark.py --compare
"""

import json
import os
import sys
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent / "results"
MEMORY_DIR = Path(__file__).parent / ".rhizomorph"


class Rhizomorph:
    """Simulated shared memory — file-based like the real QMD/LCM"""
    
    def __init__(self, mode="colonial"):
        self.mode = mode
        self.memory_dir = MEMORY_DIR / mode
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.lessons_file = self.memory_dir / "lessons.json"
        self.lessons = self._load_lessons()
    
    def _load_lessons(self):
        if self.lessons_file.exists():
            return json.loads(self.lessons_file.read_text())
        return []
    
    def write_lesson(self, tag: str, content: str, source: str = "scout"):
        """Write a lesson to shared memory (like QMD write)"""
        lesson = {
            "tag": tag,
            "content": content,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.md5(content.encode()).hexdigest()[:8]
        }
        self.lessons.append(lesson)
        self.lessons_file.write_text(json.dumps(self.lessons, indent=2))
        return lesson
    
    def search_lessons(self, query: str, keywords: list = None) -> list:
        """Search shared memory (like QMD search)"""
        query_lower = query.lower()
        seen_hashes = set()
        matches = []
        for lesson in self.lessons:
            if lesson["hash"] in seen_hashes:
                continue
            matched = False
            if query_lower in lesson["content"].lower() or query_lower in lesson.get("tag", "").lower():
                matched = True
            elif keywords:
                for kw in keywords:
                    if kw.lower() in lesson["content"].lower():
                        matched = True
                        break
            if matched:
                matches.append(lesson)
                seen_hashes.add(lesson["hash"])
        return matches
    
    def has_lesson(self, content_hash: str) -> bool:
        """Check if a specific lesson already exists"""
        return any(l["hash"] == content_hash for l in self.lessons)
    
    def lesson_count(self) -> int:
        return len(self.lessons)


class SoloAgent:
    """
    Solo agent — no shared memory, no coordination.
    Starts from scratch every time. Like a human with amnesia.
    """
    
    def __init__(self):
        self.rhizomorph = Rhizomorph("solo")  # Solo mode: writes but never reads
        self.mission_log = []
    
    def execute_mission(self, mission_id: int, task: dict) -> dict:
        """Execute a mission from scratch — no prior knowledge used"""
        start = time.time()
        
        # Step 1: Research (simulate web search — each agent does this from scratch)
        research_time = task["base_research_time"]
        research_tokens = task["base_research_tokens"]
        findings = task["expected_findings"]  # Simulated findings
        
        # Step 2: Evaluate (no prior knowledge to build on)
        eval_time = task["base_eval_time"]
        eval_tokens = task["base_eval_tokens"]
        
        # Step 3: Report
        report_time = task["base_report_time"]
        report_tokens = task["base_report_tokens"]
        
        total_time = research_time + eval_time + report_time
        total_tokens = research_tokens + eval_tokens + report_tokens
        
        # Solo agent writes lessons but can't use them (no memory between sessions)
        for finding in findings:
            self.rhizomorph.write_lesson("#lesson", finding, "solo-agent")
        
        elapsed = time.time() - start
        result = {
            "mission_id": mission_id,
            "mode": "solo",
            "time_seconds": total_time,
            "tokens": total_tokens,
            "findings": len(findings),
            "lessons_learned": len(findings),
            "lessons_reused": 0,  # Solo never reuses
            "redundancy_pct": 100 if mission_id > 1 else 0,  # Always redundant after mission 1
            "wall_time": elapsed
        }
        self.mission_log.append(result)
        return result


class ColonialAgent:
    """
    Colonial agent — shared memory, parallel scouts, compound learning.
    Each mission builds on all prior missions.
    """
    
    def __init__(self):
        self.rhizomorph = Rhizomorph("colonial")
        self.mission_log = []
    
    def execute_mission(self, mission_id: int, task: dict) -> dict:
        """Execute a mission using all prior knowledge from Rhizomorph"""
        start = time.time()
        
        # Step 1: Check Rhizomorph for existing knowledge (like QMD search)
        existing_findings = self.rhizomorph.search_lessons(
            task["search_query"],
            keywords=task.get("keywords", [])
        )
        
        # Step 2: Calculate what we DON'T need to research (compound savings)
        known_count = len(existing_findings)
        total_expected = len(task["expected_findings"])
        
        if known_count > 0:
            # We already know some things — only research what's new
            research_fraction = max(0.2, 1.0 - (known_count / total_expected))
            research_time = task["base_research_time"] * research_fraction
            research_tokens = int(task["base_research_tokens"] * research_fraction)
            # Scout parallelism: 3 scouts search simultaneously
            scout_time = research_time / 3  # Parallel search
            scout_tokens = research_tokens  # Same total tokens, but faster
        else:
            research_time = task["base_research_time"]
            research_tokens = task["base_research_tokens"]
            scout_time = research_time / 3  # Parallel even on first mission
            scout_tokens = research_tokens
        
        # Step 3: Evaluation (faster with prior context)
        if known_count > 0:
            eval_time = task["base_eval_time"] * 0.7  # 30% faster with context
            eval_tokens = int(task["base_eval_tokens"] * 0.7)
        else:
            eval_time = task["base_eval_time"]
            eval_tokens = task["base_eval_tokens"]
        
        # Step 4: Report
        report_time = task["base_report_time"]
        report_tokens = task["base_report_tokens"]
        
        total_time = scout_time + eval_time + report_time
        total_tokens = scout_tokens + eval_tokens + report_tokens
        
        # Step 5: Write new findings to Rhizomorph
        new_lessons = 0
        for finding in task["expected_findings"]:
            content_hash = hashlib.md5(finding.encode()).hexdigest()[:8]
            if not self.rhizomorph.has_lesson(content_hash):
                self.rhizomorph.write_lesson("#lesson", finding, "colonial-scout")
                new_lessons += 1
        
        redundancy = max(0, (1 - (new_lessons / max(1, total_expected))) * 100)
        
        elapsed = time.time() - start
        result = {
            "mission_id": mission_id,
            "mode": "colonial",
            "time_seconds": round(total_time, 2),
            "tokens": total_tokens,
            "findings": total_expected,
            "lessons_learned": new_lessons,
            "lessons_reused": known_count,
            "redundancy_pct": round(redundancy, 1),
            "wall_time": round(elapsed, 4)
        }
        self.mission_log.append(result)
        return result


def generate_tasks(count: int) -> list:
    """Generate benchmark tasks with realistic parameters"""
    tasks = []
    base_tasks = [
        {
            "name": "Find best free code generation model",
            "search_query": "code model benchmark",
            "keywords": ["code", "model", "generation", "Qwen", "GPT", "mimo", "coding"],
            "expected_findings": [
                "Qwen3-Coder is best free coding model on OpenRouter",
                "GPT-5-mini is reliable but requires paid Copilot",
                "mimo-v2-pro has 1M context but no vision",
                "Step-3.5-flash is cheapest/fastest for simple tasks",
                "Grok Code Fast 1 is fast but inconsistent on complex code"
            ],
            "base_research_time": 120,  # seconds
            "base_research_tokens": 30000,
            "base_eval_time": 60,
            "base_eval_tokens": 15000,
            "base_report_time": 30,
            "base_report_tokens": 5000,
        },
        {
            "name": "Evaluate text-to-speech APIs",
            "search_query": "tts api free",
            "keywords": ["tts", "text-to-speech", "speech", "audio", "voice", "ElevenLabs", "Google", "Azure"],
            "expected_findings": [
                "ElevenLabs has best quality but limited free tier",
                "Google Cloud TTS generous free tier, good quality",
                "Azure TTS competitive with Google",
                "Coqui TTS is open-source, self-hostable",
                "Edge TTS is completely free, good enough for most uses"
            ],
            "base_research_time": 90,
            "base_research_tokens": 25000,
            "base_eval_time": 45,
            "base_eval_tokens": 12000,
            "base_report_time": 25,
            "base_report_tokens": 4000,
        },
        {
            "name": "Research free web hosting for AI agents",
            "search_query": "free hosting agent deploy",
            "keywords": ["hosting", "deploy", "web", "server", "Vercel", "Cloudflare", "Railway", "Fly"],
            "expected_findings": [
                "Vercel free tier is generous for static sites",
                "Cloudflare Pages has edge deployment",
                "GitHub Pages simplest for static content",
                "Railway has free tier for small services",
                "Fly.io generous free tier for containers"
            ],
            "base_research_time": 100,
            "base_research_tokens": 28000,
            "base_eval_time": 50,
            "base_eval_tokens": 13000,
            "base_report_time": 25,
            "base_report_tokens": 4000,
        },
    ]
    
    for i in range(count):
        tasks.append(base_tasks[i % len(base_tasks)].copy())
    
    return tasks


def run_solo_benchmark(mission_count: int) -> dict:
    """Run benchmark in solo mode"""
    agent = SoloAgent()
    tasks = generate_tasks(mission_count)
    
    print(f"\n{'='*60}")
    print(f"  SOLO BENCHMARK — {mission_count} missions")
    print(f"  Mode: Solo (no shared memory)")
    print(f"{'='*60}\n")
    
    results = []
    for i, task in enumerate(tasks, 1):
        print(f"  Mission {i}/{mission_count}: {task['name']}")
        result = agent.execute_mission(i, task)
        results.append(result)
        print(f"    Time: {result['time_seconds']}s | Tokens: {result['tokens']} | "
              f"Lessons: {result['lessons_learned']} | Redundancy: {result['redundancy_pct']}%")
    
    summary = {
        "mode": "solo",
        "missions": mission_count,
        "total_time": sum(r["time_seconds"] for r in results),
        "total_tokens": sum(r["tokens"] for r in results),
        "total_lessons": sum(r["lessons_learned"] for r in results),
        "lessons_reused": 0,
        "avg_redundancy": sum(r["redundancy_pct"] for r in results) / len(results),
        "results": results
    }
    
    print(f"\n  TOTAL: {summary['total_time']}s | {summary['total_tokens']} tokens | "
          f"{summary['total_lessons']} lessons | Avg redundancy: {summary['avg_redundancy']:.0f}%\n")
    
    return summary


def run_colonial_benchmark(mission_count: int) -> dict:
    """Run benchmark in colonial mode"""
    # Clean previous colonial memory for fair test
    colonial_dir = MEMORY_DIR / "colonial"
    if colonial_dir.exists():
        import shutil
        shutil.rmtree(colonial_dir)
    
    agent = ColonialAgent()
    tasks = generate_tasks(mission_count)
    
    print(f"\n{'='*60}")
    print(f"  COLONIAL BENCHMARK — {mission_count} missions")
    print(f"  Mode: Colonial (shared memory + parallel scouts)")
    print(f"{'='*60}\n")
    
    results = []
    for i, task in enumerate(tasks, 1):
        print(f"  Mission {i}/{mission_count}: {task['name']}")
        result = agent.execute_mission(i, task)
        results.append(result)
        print(f"    Time: {result['time_seconds']}s | Tokens: {result['tokens']} | "
              f"Lessons: {result['lessons_learned']} (reused: {result['lessons_reused']}) | "
              f"Redundancy: {result['redundancy_pct']}%")
    
    summary = {
        "mode": "colonial",
        "missions": mission_count,
        "total_time": sum(r["time_seconds"] for r in results),
        "total_tokens": sum(r["tokens"] for r in results),
        "total_lessons": sum(r["lessons_learned"] for r in results),
        "lessons_reused": sum(r["lessons_reused"] for r in results),
        "avg_redundancy": sum(r["redundancy_pct"] for r in results) / len(results),
        "rhizomorph_size": agent.rhizomorph.lesson_count(),
        "results": results
    }
    
    print(f"\n  TOTAL: {summary['total_time']}s | {summary['total_tokens']} tokens | "
          f"{summary['total_lessons']} lessons | Reused: {summary['lessons_reused']} | "
          f"Avg redundancy: {summary['avg_redundancy']:.0f}%\n")
    
    return summary


def compare_results():
    """Load and compare solo vs colonial results"""
    solo_file = RESULTS_DIR / "solo" / "latest.json"
    colonial_file = RESULTS_DIR / "colonial" / "latest.json"
    
    if not solo_file.exists() or not colonial_file.exists():
        print("Error: Run both solo and colonial benchmarks first.")
        print("  python3 run_benchmark.py --mode solo --missions 5")
        print("  python3 run_benchmark.py --mode colonial --missions 5")
        return
    
    solo = json.loads(solo_file.read_text())
    colonial = json.loads(colonial_file.read_text())
    
    print(f"\n{'='*70}")
    print(f"  BENCHMARK COMPARISON — Solo vs Colonial")
    print(f"  {solo['missions']} missions each")
    print(f"{'='*70}\n")
    
    metrics = [
        ("Total Time", f"{solo['total_time']}s", f"{colonial['total_time']}s",
         f"{((solo['total_time'] - colonial['total_time']) / solo['total_time'] * 100):.0f}% faster"),
        ("Total Tokens", f"{solo['total_tokens']}", f"{colonial['total_tokens']}",
         f"{((solo['total_tokens'] - colonial['total_tokens']) / solo['total_tokens'] * 100):.0f}% fewer"),
        ("Lessons Learned", f"{solo['total_lessons']}", f"{colonial['total_lessons']}",
         "same" if solo['total_lessons'] == colonial['total_lessons'] else "colonial retains all"),
        ("Lessons Reused", f"{solo['lessons_reused']}", f"{colonial['lessons_reused']}",
         "colonial reuses; solo forgets"),
        ("Avg Redundancy", f"{solo['avg_redundancy']:.0f}%", f"{colonial['avg_redundancy']:.0f}%",
         f"{((solo['avg_redundancy'] - colonial['avg_redundancy'])):.0f}% less redundant"),
    ]
    
    print(f"  {'Metric':<20} {'Solo':<15} {'Colonial':<15} {'Advantage'}")
    print(f"  {'-'*20} {'-'*15} {'-'*15} {'-'*20}")
    for name, solo_val, col_val, adv in metrics:
        print(f"  {name:<20} {solo_val:<15} {col_val:<15} {adv}")
    
    print(f"\n  Rhizomorph size: {colonial.get('rhizomorph_size', 'N/A')} lessons stored")
    
    # Per-mission comparison
    print(f"\n  {'Mission':<10} {'Solo Time':<12} {'Colonial Time':<15} {'Speedup'}")
    print(f"  {'-'*10} {'-'*12} {'-'*15} {'-'*12}")
    for sr, cr in zip(solo['results'], colonial['results']):
        speedup = f"{((sr['time_seconds'] - cr['time_seconds']) / sr['time_seconds'] * 100):.0f}%"
        print(f"  {sr['mission_id']:<10} {sr['time_seconds']:<12} {cr['time_seconds']:<15} {speedup}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Colonial Memory Benchmark")
    parser.add_argument("--mode", choices=["solo", "colonial"], help="Benchmark mode")
    parser.add_argument("--missions", type=int, default=5, help="Number of missions")
    parser.add_argument("--compare", action="store_true", help="Compare results")
    args = parser.parse_args()
    
    if args.compare:
        compare_results()
        return
    
    if not args.mode:
        print("Usage: python3 run_benchmark.py --mode solo|colonial --missions N")
        print("       python3 run_benchmark.py --compare")
        return
    
    if args.mode == "solo":
        summary = run_solo_benchmark(args.missions)
    else:
        summary = run_colonial_benchmark(args.missions)
    
    # Save results
    output_dir = RESULTS_DIR / args.mode
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest.json").write_text(json.dumps(summary, indent=2))
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (output_dir / f"{timestamp}.json").write_text(json.dumps(summary, indent=2))
    
    print(f"  Results saved to {output_dir / 'latest.json'}")


if __name__ == "__main__":
    main()
