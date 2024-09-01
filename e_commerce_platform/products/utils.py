import csv
from io import StringIO
from .models import Product


def export_to_csv(data):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output


def generate_summary():
    categories = Product.objects.values("category").distinct()
    summary_data = []

    for category in categories:
        category_name = category["category"]
        products = Product.objects.filter(category=category_name)

        total_revenue = sum([product.price * product.quantity_sold for product in products])
        top_product = max(products, key=lambda p: p.quantity_sold)

        summary_data.append({
            "category": category_name,
            "total_revenue": total_revenue,
            "top_product": top_product.product_name,
            "top_product_quantity_sold": top_product.quantity_sold
        })

    summary = export_to_csv(summary_data)
    return summary
