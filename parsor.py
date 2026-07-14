import json
import re
from pathlib import Path
from parsel import Selector

base_url = "https://www.nykaa.com/"


def extract_preloaded_state(html):
    selector = Selector(text=html)
    script_text = next(
        (
            s
            for s in selector.xpath("//script/text()").getall()
            if "window.__PRELOADED_STATE__" in s
        ),
        None,
    )
    if script_text is None:
        print("window.__PRELOADED_STATE__ not found.")
        return None

    match = re.search(r"window\.__PRELOADED_STATE__\s*=\s*", script_text)
    if not match:
        print("Assignment not found.")
        return None

    start = match.end()
    try:
        obj, _ = json.JSONDecoder().raw_decode(script_text, start)
        return obj
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return None


def parse_products(data):
    products = []
    product_data = (
        data.get("categoryListing", {}).get("listingData", {}).get("products", []) or []
    )

    for product in product_data:
        try:
            sale = product.get("cohortSaleTemplate") or {}
            products.append(
                {
                    "product_id": product.get("productId", ""),
                    "sku": product.get("sku", ""),
                    "slug": base_url + product.get("slug", ""),
                    "product_name": product.get("productTitle", ""),
                    "brand_name": product.get("brandName", ""),
                    "price": product.get("price", 0),
                    "original_price": product.get("mrp", 0),
                    "offer": product.get("offer", ""),
                    "image_url": product.get("imageUrl", ""),
                    "in_stock": product.get("inStock", False),
                    "rating": product.get("rating", 0),
                    "rating_count": product.get("ratingCount", 0),
                    "quantity": product.get("quantity", 0),
                    "discount": product.get("discount", 0),
                    "new_tags": [
                        tag.get("title", "") for tag in (product.get("newTags") or [])
                    ],
                    "sale": {
                        "sale_price": sale.get("price", 0),
                        "text": sale.get("text", ""),
                        "sale_discount": sale.get("discount", 0),
                    },
                    "most_reordered": bool(product.get("secondaryTag")),
                }
            )
        except Exception as e:
            continue
    return products


def process_html_file(html_file, output_dir):
    print(f"Processing: {html_file.name}")

    html = html_file.read_text(encoding="utf-8")
    data = extract_preloaded_state(html)

    if data is None:
        return

    products = parse_products(data)

    output_file = output_dir / f"{html_file.stem}.json"
    output_file.write_text(
        json.dumps(products, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✅ Saved: {output_file.name}\n")


def main():
    input_dir = Path(r"C:\Users\parth.khatri\Desktop\github\nykaa-request")
    output_dir = input_dir / "output"

    output_dir.mkdir(exist_ok=True)

    html_files = sorted(input_dir.glob("*.html"))

    if not html_files:
        print("No HTML files found.")
        return

    print(f"Found {len(html_files)} HTML file(s).\n")

    for html_file in html_files:
        process_html_file(html_file, output_dir)


if __name__ == "__main__":
    main()
