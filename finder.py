import requests
from typing import List, Dict

DEX_SCREENER_BASE = "https://api.dexscreener.com/latest/dex/pairs"

# =========================
# PARAMETRI CONFIGURABILI
# =========================
CHAIN = "bsc"                  # es: bsc, ethereum, base, polygon
DEX_FILTER = "pancakeswap"     # None per accettare tutti i DEX

LIQUIDITY_MIN = 500_000        # USD
LIQUIDITY_MAX = 5_000_000      # USD

VOLUME_7D_MIN = 500            # USD (settimanale)

# =========================
# FUNZIONI
# =========================

def fetch_pairs(chain: str) -> List[Dict]:
    url = f"{DEX_SCREENER_BASE}/{chain}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("pairs", [])


def pool_matches_criteria(pair: Dict) -> bool:
    liquidity = pair.get("liquidity", {}).get("usd", 0)
    volume_7d = pair.get("volume", {}).get("h7d", 0)

    if not (LIQUIDITY_MIN <= liquidity <= LIQUIDITY_MAX):
        return False

    if volume_7d < VOLUME_7D_MIN:
        return False

    if DEX_FILTER:
        if pair.get("dexId") != DEX_FILTER:
            return False

    return True


def normalize_pair(pair: Dict) -> Dict:
    return {
        "chain": pair.get("chainId"),
        "dex": pair.get("dexId"),
        "pair_address": pair.get("pairAddress"),
        "base_token": pair.get("baseToken", {}).get("symbol"),
        "quote_token": pair.get("quoteToken", {}).get("symbol"),
        "liquidity_usd": pair.get("liquidity", {}).get("usd"),
        "volume_24h": pair.get("volume", {}).get("h24"),
        "volume_7d": pair.get("volume", {}).get("h7d"),
        "price_usd": pair.get("priceUsd"),
    }


def main():
    print(f"Fetching pools for chain: {CHAIN}")
    pairs = fetch_pairs(CHAIN)
    print(f"Total pools retrieved: {len(pairs)}")

    selected = []
    for pair in pairs:
        if pool_matches_criteria(pair):
            selected.append(normalize_pair(pair))

    print(f"Pools matching criteria: {len(selected)}\n")

    for p in selected:
        print(
            f"{p['base_token']}/{p['quote_token']} | "
            f"DEX: {p['dex']} | "
            f"Liquidity: ${p['liquidity_usd']:,.0f} | "
            f"Vol 7d: ${p['volume_7d']:,.0f}"
        )


if __name__ == "__main__":
    main()
