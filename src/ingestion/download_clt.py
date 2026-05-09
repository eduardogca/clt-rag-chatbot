import urllib.request
from pathlib import Path

URL = "https://sindhosfilvp.com.br/wp-content/uploads/2024/06/consolidacao_leis_trabalho_4ed-atualizada.pdf"
OUTPUT = Path("data/raw/clt.pdf")


def download(url: str = URL, output: Path = OUTPUT) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        print(f"PDF already exists at {output}, skipping download.")
        return
    print(f"Downloading CLT PDF...")
    urllib.request.urlretrieve(url, output)
    size_mb = output.stat().st_size / 1_048_576
    print(f"Saved {output} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    download()
