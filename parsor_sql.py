import json
import time
from pathlib import Path
import requests
import mysql.connector
from mysql.connector import Error

base_url = "https://www.nykaa.com/"
API_URL = "https://www.nykaa.com/app-api/index.php/products/list"

HEADERS = {
    # ... keep your existing headers dict here (incl. Cookie / x-csrf-token) ...
}

# ---- MySQL connection settings ----
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",  # <-- update this
    "database": "nykaa_scraper",  # <-- create this database beforehand
}


def fetch_page(category_id, page_no, session):
    params = {"category_id": category_id, "page_no": page_no}
    resp = session.get(API_URL, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("response", payload)


def extract_pagination_info(data):
    total_found = data.get("total_found")
    product_count = data.get("product_count")
    return total_found, product_count


def extract_raw_products(data):
    return data.get("products") or []


def parse_products(product_data):
    products = []
    for product in product_data or []:
        try:
            sale = product.get("cohort_sale_template") or {}
            products.append(
                {
                    "id": product.get("id", ""),
                    "sku": product.get("sku", ""),
                    "slug": base_url + product.get("slug", ""),
                    "product_name": product.get("product_title", ""),
                    "brand_name": product.get("brand_name", ""),
                    "price": product.get("final_price", 0),
                    "original_price": product.get("price", 0),
                    "offer": product.get("offer_message", ""),
                    "image_url": product.get("image_url", ""),
                    "in_stock": product.get("is_saleable", False),
                    "rating": product.get("rating", 0),
                    "rating_count": product.get("rating_count", 0),
                    "quantity": product.get("quantity", 0),
                    "discount": product.get("discount", 0),
                    "new_tags": [
                        tag.get("title", "") for tag in (product.get("pdt_tags") or [])
                    ],
                    "sale": {
                        "sale_price": sale.get("price", 0),
                        "text": sale.get("text", ""),
                        "sale_discount": sale.get("sub_heading", 0),
                    },
                    "most_reordered": bool(product.get("secondary_tags")),
                }
            )
        except Exception:
            continue
    return products


# ---------------- MySQL helpers ----------------

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id                VARCHAR(50)  PRIMARY KEY,
    sku               VARCHAR(50),
    slug              VARCHAR(500),
    product_name      VARCHAR(500),
    brand_name        VARCHAR(255),
    price             DECIMAL(10,2) DEFAULT 0,
    original_price    DECIMAL(10,2) DEFAULT 0,
    offer             VARCHAR(255),
    image_url         VARCHAR(500),
    in_stock          BOOLEAN DEFAULT FALSE,
    rating            FLOAT DEFAULT 0,
    rating_count      INT DEFAULT 0,
    quantity          INT DEFAULT 0,
    discount          FLOAT DEFAULT 0,
    new_tags          JSON,
    sale_price        DECIMAL(10,2) DEFAULT 0,
    sale_text         VARCHAR(255),
    sale_discount     VARCHAR(255),
    most_reordered    BOOLEAN DEFAULT FALSE,
    category_id       VARCHAR(50),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

UPSERT_SQL = """
INSERT INTO products (
    id, sku, slug, product_name, brand_name, price, original_price,
    offer, image_url, in_stock, rating, rating_count, quantity, discount,
    new_tags, sale_price, sale_text, sale_discount, most_reordered, category_id
) VALUES (
    %(id)s, %(sku)s, %(slug)s, %(product_name)s, %(brand_name)s,
    %(price)s, %(original_price)s, %(offer)s, %(image_url)s, %(in_stock)s,
    %(rating)s, %(rating_count)s, %(quantity)s, %(discount)s, %(new_tags)s,
    %(sale_price)s, %(sale_text)s, %(sale_discount)s, %(most_reordered)s, %(category_id)s
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
    most_reordered = VALUES(most_reordered),
    category_id = VALUES(category_id);
"""


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def ensure_table(conn):
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    cursor.close()


def save_products_to_mysql(conn, products, category_id):
    if not products:
        return 0

    rows = []
    for p in products:
        if not p.get("id"):
            continue
        rows.append(
            {
                "id": p["id"],
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
                "category_id": category_id,
            }
        )

    if not rows:
        return 0

    cursor = conn.cursor()
    cursor.executemany(UPSERT_SQL, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    return affected



def scrape_category(category_id, output_dir, conn):
    session = requests.Session()
    all_products = []

    print(f"Fetching page 1 for category_id={category_id} ...")
    first_page = fetch_page(category_id, 1, session)

    total_found, product_count = extract_pagination_info(first_page)

    if not total_found or not product_count:
        print("⚠️  Could not auto-detect total_found/product_count.")
        print("Top-level keys in response:", list(first_page.keys()))
        return

    total_pages = -(-total_found // product_count)  # ceil division
    print(
        f"total_found={total_found}, product_count={product_count}, total_pages={total_pages}\n"
    )

    page1_products = parse_products(extract_raw_products(first_page))
    all_products.extend(page1_products)
    saved = save_products_to_mysql(conn, page1_products, category_id)
    print(
        f"  Page 1/{total_pages}: {len(page1_products)} product(s), {saved} saved to MySQL"
    )

    for page_no in range(2, total_pages + 1):
        time.sleep(1)
        page_data = fetch_page(category_id, page_no, session)
        page_products = parse_products(extract_raw_products(page_data))
        all_products.extend(page_products)

        try:
            saved = save_products_to_mysql(conn, page_products, category_id)
            print(
                f"  Page {page_no}/{total_pages}: +{len(page_products)} "
                f"(total {len(all_products)}), {saved} saved to MySQL"
            )
        except Error as e:
            print(f"  ❌ MySQL error on page {page_no}: {e}")

    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"category_{category_id}.json"
    output_file.write_text(
        json.dumps(all_products, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n✅ Done. Saved {len(all_products)} product(s) to MySQL and {output_file}")


def main():
    category_id = input("Enter category_id: ").strip()
    output_dir = Path("output_data")

    try:
        conn = get_connection()
    except Error as e:
        print(f"❌ Could not connect to MySQL: {e}")
        return

    ensure_table(conn)
    scrape_category(category_id, output_dir, conn)
    conn.close()


if __name__ == "__main__":
    main()