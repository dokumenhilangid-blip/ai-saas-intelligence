import json
import os
from datetime import datetime, timedelta
from collections import Counter
from backend.database import get_connection, get_tools, get_stats

class SherlockAnalyzer:
    """
    Sherlock Analysis Framework
    Mendeteksi pola, tren, dan peluang dari data AI tools
    """

    def __init__(self):
        self.conn = None

    def run_full_analysis(self) -> dict:
        print("\n[Sherlock] 🔍 Starting full analysis...")
        tools = get_tools(limit=500)
        stats = get_stats()

        if not tools:
            return {"error": "No data to analyze. Run scraper first."}

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_tools_analyzed": len(tools),
            "velocity": self._analyze_velocity(tools),
            "category_dominance": self._analyze_categories(tools),
            "source_breakdown": self._analyze_sources(tools),
            "momentum_tools": self._find_momentum_tools(tools),
            "whitespace": self._find_whitespace(tools),
            "pricing_landscape": self._analyze_pricing(tools),
            "indonesia_opportunities": self._indonesia_filter(tools),
            "signals": self._extract_signals(tools)
        }

        self._save_report(report)
        print("[Sherlock] ✅ Analysis complete")
        return report

    def _analyze_velocity(self, tools: list) -> dict:
        """Berapa banyak tools baru per hari/minggu"""
        now = datetime.utcnow()
        last_24h = 0
        last_7d = 0
        last_30d = 0

        for t in tools:
            first_seen = t.get("first_seen", "")
            if not first_seen:
                continue
            try:
                dt = datetime.fromisoformat(first_seen)
                diff = now - dt
                if diff.days < 1:
                    last_24h += 1
                if diff.days < 7:
                    last_7d += 1
                if diff.days < 30:
                    last_30d += 1
            except:
                continue

        return {
            "last_24h": last_24h,
            "last_7d": last_7d,
            "last_30d": last_30d,
            "avg_per_day": round(last_30d / 30, 1) if last_30d else 0
        }

    def _analyze_categories(self, tools: list) -> dict:
        """Kategori mana yang paling banyak tools-nya"""
        categories = []
        for t in tools:
            cat = t.get("category")
            if cat:
                categories.append(cat.lower().strip())

        counter = Counter(categories)
        total = len(categories)

        return {
            "top_10": [
                {
                    "category": cat,
                    "count": count,
                    "percentage": round(count / total * 100, 1) if total else 0
                }
                for cat, count in counter.most_common(10)
            ],
            "total_categories": len(counter),
            "uncategorized": len([t for t in tools if not t.get("category")])
        }

    def _analyze_sources(self, tools: list) -> dict:
        """Breakdown tools per source"""
        sources = Counter([t.get("source", "unknown") for t in tools])
        return {
            "breakdown": dict(sources),
            "most_active": sources.most_common(1)[0][0] if sources else None,
            "total_sources": len(sources)
        }

    def _find_momentum_tools(self, tools: list) -> list:
        """Tools dengan upvotes/comments tinggi = momentum pasar"""
        scored = []
        for t in tools:
            upvotes = t.get("upvotes") or 0
            comments = t.get("comments") or 0
            score = (upvotes * 1.0) + (comments * 0.5)
            if score > 0:
                scored.append({
                    "name": t.get("name"),
                    "score": score,
                    "upvotes": upvotes,
                    "comments": comments,
                    "source": t.get("source"),
                    "category": t.get("category"),
                    "url": t.get("url")
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:15]

    def _find_whitespace(self, tools: list) -> dict:
        """
        Whitespace = kategori yang SEDIKIT tools-nya
        = peluang untuk builder baru
        """
        all_categories = [
            "writing", "coding", "image", "video", "audio",
            "marketing", "productivity", "research",
            "customer-service", "data-analysis", "finance",
            "education", "health", "legal", "hr"
        ]

        category_counts = Counter([
            (t.get("category") or "").lower()
            for t in tools
        ])

        underserved = []
        for cat in all_categories:
            count = category_counts.get(cat, 0)
            if count < 5:
                underserved.append({
                    "category": cat,
                    "existing_tools": count,
                    "opportunity_score": "HIGH" if count == 0 else "MEDIUM"
                })

        return {
            "underserved_categories": underserved,
            "total_whitespace_areas": len(underserved)
        }

    def _analyze_pricing(self, tools: list) -> dict:
        """Pola pricing di pasar"""
        pricing_data = []
        for t in tools:
            pricing = (t.get("pricing") or "").lower()
            if pricing:
                pricing_data.append(pricing)

        if not pricing_data:
            return {"note": "No pricing data available yet"}

        free_count = sum(1 for p in pricing_data if "free" in p)
        freemium = sum(1 for p in pricing_data if "freemium" in p)
        paid = sum(1 for p in pricing_data if any(x in p for x in ["paid", "$", "pro", "premium"]))

        total = len(pricing_data)
        return {
            "free": {"count": free_count, "pct": round(free_count/total*100, 1)},
            "freemium": {"count": freemium, "pct": round(freemium/total*100, 1)},
            "paid": {"count": paid, "pct": round(paid/total*100, 1)},
            "total_with_pricing": total
        }

    def _indonesia_filter(self, tools: list) -> list:
        """
        Filter tools yang relevan untuk pasar Indonesia/SME
        Berdasarkan kategori dan deskripsi
        """
        indonesia_keywords = [
            "small business", "sme", "ecommerce", "social media",
            "content", "marketing", "customer", "invoice",
            "productivity", "writing", "translation", "chatbot",
            "whatsapp", "instagram", "tiktok"
        ]

        relevant = []
        for t in tools:
            desc = (t.get("description") or "").lower()
            name = (t.get("name") or "").lower()
            cat = (t.get("category") or "").lower()

            score = 0
            matched_keywords = []
            for kw in indonesia_keywords:
                if kw in desc or kw in name or kw in cat:
                    score += 1
                    matched_keywords.append(kw)

            if score >= 1:
                relevant.append({
                    "name": t.get("name"),
                    "description": (t.get("description") or "")[:150],
                    "category": t.get("category"),
                    "relevance_score": score,
                    "matched_keywords": matched_keywords,
                    "url": t.get("url")
                })

        relevant.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant[:20]

    def _extract_signals(self, tools: list) -> list:
        """
        Market signals = pattern yang muncul berulang
        """
        signals = []
        total = len(tools)

        # Signal 1: Volume
        if total > 100:
            signals.append({
                "type": "volume",
                "signal": f"High data volume: {total} tools tracked",
                "strength": "strong"
            })

        # Signal 2: Dominant categories
        cats = Counter([t.get("category", "") for t in tools if t.get("category")])
        if cats:
            top_cat, top_count = cats.most_common(1)[0]
            pct = round(top_count / total * 100, 1)
            if pct > 20:
                signals.append({
                    "type": "category_dominance",
                    "signal": f"{top_cat} dominates at {pct}% of all tools",
                    "strength": "strong"
                })

        # Signal 3: Multi-source validation
        sources = Counter([t.get("source", "") for t in tools])
        if len(sources) >= 3:
            signals.append({
                "type": "multi_source",
                "signal": f"Data validated across {len(sources)} sources",
                "strength": "medium"
            })

        # Signal 4: High engagement tools
        high_engagement = [t for t in tools if (t.get("upvotes") or 0) > 100]
        if high_engagement:
            signals.append({
                "type": "engagement",
                "signal": f"{len(high_engagement)} tools with 100+ upvotes detected",
                "strength": "strong"
            })

        return signals

    def _save_report(self, report: dict):
        """Simpan report ke database"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO insights (title, content, insight_type, generated_at, model_used)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"Sherlock Report {datetime.utcnow().strftime('%Y-%m-%d')}",
                json.dumps(report),
                "sherlock_analysis",
                report["generated_at"],
                "sherlock-v1"
            ))
            conn.commit()
            print("[Sherlock] Report saved to database")
        except Exception as e:
            print(f"[Sherlock] Save error: {e}")
        finally:
            conn.close()
