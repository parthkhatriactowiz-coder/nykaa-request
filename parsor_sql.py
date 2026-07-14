import json
import re
from pathlib import Path
from parsel import Selector
import mysql.connector
from mysql.connector import Error

base_url = "https://www.nykaa.com/"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",   
    "database": "nykaa_scraper",
}


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
        except Exception:
            continue
    return products


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS products (
    product_id       VARCHAR(50)  PRIMARY KEY,
    sku              VARCHAR(50),
    slug             VARCHAR(500),
    product_name     VARCHAR(500),
    brand_name       VARCHAR(255),
    price            DECIMAL(10,2) DEFAULT 0,
    original_price   DECIMAL(10,2) DEFAULT 0,
    offer            VARCHAR(255),
    image_url        VARCHAR(500),
    in_stock         BOOLEAN DEFAULT FALSE,
    rating           FLOAT DEFAULT 0,
    rating_count     INT DEFAULT 0,
    quantity         INT DEFAULT 0,
    discount         FLOAT DEFAULT 0,
    new_tags         JSON,
    sale_price       DECIMAL(10,2) DEFAULT 0,
    sale_text        VARCHAR(255),
    sale_discount    FLOAT DEFAULT 0,
    most_reordered   BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

UPSERT_SQL = """
INSERT INTO products (
    product_id, sku, slug, product_name, brand_name, price, original_price,
    offer, image_url, in_stock, rating, rating_count, quantity, discount,
    new_tags, sale_price, sale_text, sale_discount, most_reordered
) VALUES (
    %(product_id)s, %(sku)s, %(slug)s, %(product_name)s, %(brand_name)s,
    %(price)s, %(original_price)s, %(offer)s, %(image_url)s, %(in_stock)s,
    %(rating)s, %(rating_count)s, %(quantity)s, %(discount)s, %(new_tags)s,
    %(sale_price)s, %(sale_text)s, %(sale_discount)s, %(most_reordered)s
)
ON DUPLICATE KEY UPDATE
    sku = VALUES(sku),
    slug = VALUES(slug),
    product_name = VALUES(product_name),
    brand_name = VALUES(brand_name),
    price = VALUES(price),
    original_price = VALUES(original_price),
    offer = VALUES(offer),
    image_url = VALUES(image_url),
    in_stock = VALUES(in_stock),
    rating = VALUES(rating),
    rating_count = VALUES(rating_count),
    quantity = VALUES(quantity),
    discount = VALUES(discount),
    new_tags = VALUES(new_tags),
    sale_price = VALUES(sale_price),
    sale_text = VALUES(sale_text),
    sale_discount = VALUES(sale_discount),
    most_reordered = VALUES(most_reordered);
"""


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def ensure_table(conn):
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    cursor.close()


def save_products_to_mysql(conn, products):
    if not products:
        return 0

    rows = []
    for p in products:
        rows.append(
            {
                "product_id": p["product_id"],
                "sku": p["sku"],
                "slug": p["slug"],
                "product_name": p["product_name"],
                "brand_name": p["brand_name"],
                "price": p["price"],
                "original_price": p["original_price"],
                "offer": p["offer"],
                "image_url": p["image_url"],
                "in_stock": p["in_stock"],
                "rating": p["rating"],
                "rating_count": p["rating_count"],
                "quantity": p["quantity"],
                "discount": p["discount"],
                "new_tags": json.dumps(p["new_tags"], ensure_ascii=False),
                "sale_price": p["sale"]["sale_price"],
                "sale_text": p["sale"]["text"],
                "sale_discount": p["sale"]["sale_discount"],
                "most_reordered": p["most_reordered"],
            }
        )

    cursor = conn.cursor()
    cursor.executemany(UPSERT_SQL, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected


def process_html_file(html_file, output_dir, conn):
    print(f"Processing: {html_file.name}")

    html = html_file.read_text(encoding="utf-8")
    data = extract_preloaded_state(html)

    if data is None:
        print(f"❌ Failed: {html_file.name}\n")
        return

    products = parse_products(data)

    output_file = output_dir / f"{html_file.stem}.json"
    output_file.write_text(
        json.dumps(products, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    try:
        save_products_to_mysql(conn, products)
        print(f"✅ Saved {len(products)} product(s) to MySQL and {output_file.name}\n")
    except Error as e:
        print(f"❌ MySQL error while saving {html_file.name}: {e}\n")


def main():
    input_dir = Path(r"C:\Users\parth.khatri\Desktop\github\nykaa-request")
    output_dir = input_dir / "output"
    output_dir.mkdir(exist_ok=True)

    html_files = sorted(input_dir.glob("*.html"))
    if not html_files:
        print("No HTML files found.")
        return

    print(f"Found {len(html_files)} HTML file(s).\n")

    try:
        conn = get_connection()
    except Error as e:
        print(f"❌ Could not connect to MySQL: {e}")
        return

    ensure_table(conn)

    for html_file in html_files:
        process_html_file(html_file, output_dir, conn)

    conn.close()


if __name__ == "__main__":
    main()