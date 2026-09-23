"""
Much of this file is based on stolen tech from
https://deklubben.dk/de-admin/slideshow/show/1/
As it is poorly written and makes it fairly easy to reverse engineer
"""

import html
import json
import logging
import time
import urllib
from datetime import time as dt_time
from typing import Any, Optional

import discord
from discord import app_commands as ac
from discord.ext import commands, tasks

lg = logging.getLogger(__name__)

BASE_URL = "https://deklubben.dk"
FETCH_SLIDES_URL = f"{BASE_URL}/de-admin/slideshow/fetch_slides"
FETCH_SLIDE_URL = f"{BASE_URL}/de-admin/slideshow/fetch_slide"
MEDIA_URL = f"{BASE_URL}/media/slideshow/"

# Taken from the the slideshow script
PERIOD_NAMES = {
    "0": "All-time",
    "1": "This semester",
    "2": "This month",
    "3": "This thursday",
}
UNIT_LABELS = {
    1: "stk",
    2: "kr.",
    3: "stk",
    4: "kr.",
    5: "kr.",
    6: "kr.",
    7: "L",
    8: "transaktioner",
    9: "rating",
    10: "gange",
}


def _clean_text(val: Optional[str]) -> str:
    if not val:
        return ""
    return html.unescape(val).strip()


class DEKlubbenLeaderboard(commands.Cog):
    """Cog for viewing DE-klubben live leaderboards and member stats."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._cached_data: Optional[dict[str, Any]] = None
        self._cached_users: list[str] = []
        self._cached_categories: list[str] = []
        self._cache_timestamp: float = 0
        self._cache_ttl_seconds: int = 86400  # 24 hours

        # Start scheduled background fetch loop
        self.daily_fetch.start()

    # --- Scheduled Background Tasks ---

    @tasks.loop(time=dt_time(hour=0, minute=0))
    async def daily_fetch(self):
        """Fetch fresh leaderboard data every day at midnight."""
        lg.info("Running scheduled midnight DE-klubben fetch...")
        try:
            self._fetch_slideshow_data(force=True)
            lg.info("Midnight DE-klubben fetch completed successfully.")
        except Exception as e:
            lg.error(f"Error during midnight fetch: {e}")

    @daily_fetch.before_loop
    async def before_daily_fetch(self):
        """Wait until bot is ready, then perform initial data fetch."""
        await self.bot.wait_until_ready()
        lg.info("Performing initial DE-klubben slideshow data fetch...")
        try:
            self._fetch_slideshow_data(force=True)
            lg.info("Initial DE-klubben fetch completed successfully.")
        except Exception as e:
            lg.error(f"Error during initial DE-klubben fetch: {e}")

    # --- Data Helper Methods ---

    def _get_gold_tier(self, name: str, golds: dict[str, list[str]]) -> Optional[str]:
        clean_name = _clean_text(name)
        for tier in ["gold70", "gold60", "gold50", "gold40", "gold30", "gold20", "gold10"]:
            tier_members = [_clean_text(m) for m in golds.get(tier, [])]
            if clean_name in tier_members:
                return tier
        return None

    def _get_badge_string(self, name: str, golds: dict[str, list[str]]) -> str:
        clean_name = _clean_text(name)
        tier = self._get_gold_tier(clean_name, golds)
        if tier:
            num = int(tier[4])
            return " " + "🎖️" * num
        return ""

    def _get_rank_emoji(self, rank: int) -> str:
        if rank == 1:
            return " 🥇 "
        elif rank == 2:
            return " 🥈 "
        elif rank == 3:
            return " 🥉 "
        return f"#{rank:02d}"

    def _fetch_slideshow_data(self, force: bool = False) -> dict[str, Any]:
        """Fetch slides and parse highscores from deklubben.dk with in-memory caching."""
        now = time.time()
        if not force and self._cached_data and (now - self._cache_timestamp < self._cache_ttl_seconds):
            return self._cached_data

        req = urllib.request.Request(f"{FETCH_SLIDES_URL}?slideshow=1", headers={"User-Agent": "DiscordBot-Syntax/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            slides_meta = json.loads(resp.read().decode("utf-8"))

        raw_slides_str = slides_meta.get("the_slides", "[]")
        raw_slides = json.loads(raw_slides_str) if isinstance(raw_slides_str, str) else raw_slides_str
        golds = slides_meta.get("golds", {})

        leaderboards = []
        user_set = set()

        for s in raw_slides:
            pk = s.get("pk")
            if not pk:
                continue

            slide_req = urllib.request.Request(
                f"{FETCH_SLIDE_URL}?slide_pk={pk}", headers={"User-Agent": "DiscordBot-Syntax/1.0"}
            )
            try:
                with urllib.request.urlopen(slide_req, timeout=10) as s_resp:
                    slide_data = json.loads(s_resp.read().decode("utf-8"))
            except Exception as e:
                lg.warning(f"Failed to fetch slide pk {pk}: {e}")
                continue

            if slide_data.get("type") == 1:
                # Column 1
                h1 = slide_data.get("high_one")
                p1 = str(slide_data.get("period_one", "0"))
                ht1 = slide_data.get("highscore_type_one", 3)
                if h1 and isinstance(h1, list):
                    title1 = _clean_text(h1[0].get("title", "Ukendt"))
                    leaderboards.append(
                        {
                            "title": title1,
                            "period_code": p1,
                            "period_name": PERIOD_NAMES.get(p1, f"Periode {p1}"),
                            "unit": UNIT_LABELS.get(ht1, "stk"),
                            "entries": h1[1:],
                        }
                    )
                    for item in h1[1:]:
                        n = _clean_text(item.get("name", ""))
                        if n and n != "Ukendt":
                            user_set.add(n)

                # Column 2
                h2 = slide_data.get("high_two")
                p2 = str(slide_data.get("period_two", "1"))
                ht2 = slide_data.get("highscore_type_two", 3)
                if h2 and isinstance(h2, list):
                    title2 = _clean_text(h2[0].get("title", "Ukendt"))
                    leaderboards.append(
                        {
                            "title": title2,
                            "period_code": p2,
                            "period_name": PERIOD_NAMES.get(p2, f"Periode {p2}"),
                            "unit": UNIT_LABELS.get(ht2, "stk"),
                            "entries": h2[1:],
                        }
                    )
                    for item in h2[1:]:
                        n = _clean_text(item.get("name", ""))
                        if n and n != "Ukendt":
                            user_set.add(n)
        # Precompute sorted autocomplete lists once during fetch
        self._cached_users = sorted(user_set, key=str.casefold)
        self._cached_categories = sorted(list(set(b["title"] for b in leaderboards)))

        self._cached_data = {
            "golds": golds,
            "leaderboards": leaderboards,
        }
        self._cache_timestamp = now
        return self._cached_data

    # --- Autocomplete Helper ---
    async def user_autocomplete(self, intr: discord.Interaction, current: str) -> list[ac.Choice[str]]:
        return [ac.Choice(name=u[:100], value=u[:100]) for u in self._cached_users if current.lower() in u.lower()][:25]

    async def category_autocomplete(self, intr: discord.Interaction, current: str) -> list[ac.Choice[str]]:
        return [ac.Choice(name=c, value=c) for c in self._cached_categories if current.lower() in c.lower()][:25]

    # --- Slash Commands ---
    @ac.command(name="de_leaderboard", description="Shows a leaderboard from the DE-Klubben")
    @ac.describe(category="Category / Bevarage", period="Choose Period")
    @ac.autocomplete(category=category_autocomplete)
    @ac.choices(
        period=[
            ac.Choice(name="This semester", value="1"),
            ac.Choice(name="Total (All-time)", value="0"),
        ]
    )
    async def de_leaderboard(self, intr: discord.Interaction, category: str, period: str = "1"):
        await intr.response.defer()
        try:
            data = self._fetch_slideshow_data()
        except Exception as e:
            lg.error(f"Error fetching slideshow: {e}")
            await intr.followup.send("❌ Could not fetch data from DE-Klubben :<", ephemeral=True)
            return

        matches = [
            b for b in data["leaderboards"] if category.lower() in b["title"].lower() and b["period_code"] == period
        ]
        if not matches:
            matches = [b for b in data["leaderboards"] if category.lower() in b["title"].lower()]

        if not matches:
            available = sorted(list(set(b["title"] for b in data["leaderboards"])))
            await intr.followup.send(
                f"❌ Did not find matching leaderboard for `{category}`.\n**Alternatives:** {', '.join(available)}",
                ephemeral=True,
            )
            return

        board = matches[0]
        embed = discord.Embed(
            title=f"🏆 {board['title']} 🏆",
            description=f"**Periode:** {board['period_name']}",
            color=discord.Color.blurple(),
        )

        rows = []
        for idx, item in enumerate(board["entries"][:10], start=1):
            name = _clean_text(item.get("name", "Ukendt"))
            score = item.get("sum", 0)
            rank = item.get("index", idx)
            badge = self._get_badge_string(name, data["golds"])
            rank_emoji = self._get_rank_emoji(rank)

            score_str = f"{score:.2f}" if isinstance(score, float) and not score.is_integer() else f"{int(score)}"
            rows.append(f"{rank_emoji} **{name}**{badge} — `{score_str} {board['unit']}`")

        embed.add_field(name="Leaderboard", value="\n".join(rows) or "Ingen data", inline=False)
        await intr.followup.send(embed=embed)

    @ac.command(name="de_user", description="Search for a given user across all leaderboards")
    @ac.autocomplete(name=user_autocomplete)
    @ac.describe(name="Name of user")
    async def de_profile(self, intr: discord.Interaction, name: str):
        await intr.response.defer()
        try:
            data = self._fetch_slideshow_data()
        except Exception as e:
            lg.error(f"Error fetching slideshow: {e}")
            await intr.followup.send("❌ Could not fetch data from DE-Klubben", ephemeral=True)
            return

        query = name.lower()
        records = []

        for b in data["leaderboards"]:
            for idx, item in enumerate(b["entries"], start=1):
                item_name = _clean_text(item.get("name", ""))
                if query in item_name.lower():
                    records.append(
                        {
                            "name": item_name,
                            "category": b["title"],
                            "period": b["period_name"],
                            "rank": item.get("index", idx),
                            "score": item.get("sum", 0),
                            "unit": b["unit"],
                        }
                    )

        if not records:
            await intr.followup.send(f"❌ Failed to find leaderboards with `{name}` in top 10.", ephemeral=True)
            return

        matched_name = records[0]["name"]
        badge = self._get_badge_string(matched_name, data["golds"])

        embed = discord.Embed(
            title=f"👤 User Profile: {matched_name}{badge}",
            color=discord.Color.purple(),
        )

        records.sort(key=lambda r: r["rank"])
        lines = []
        for r in records[:15]:
            assert isinstance(r["rank"], int)
            rank_emoji = self._get_rank_emoji(r["rank"])
            lines.append(f"{rank_emoji} **{r['category']}** ({r['period']}): `{r['score']} {r['unit']}`")

        embed.add_field(name="Highscore Placements", value="\n".join(lines), inline=False)
        await intr.followup.send(embed=embed)


from utils import get_guilds


async def setup(bot: commands.Bot):
    await bot.add_cog(DEKlubbenLeaderboard(bot), guilds=get_guilds())
