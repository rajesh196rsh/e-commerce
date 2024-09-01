from django.db.utils import IntegrityError
import pandas as pd
from .models import Product
from . import constants


def extract_and_clean_product_data(csv_path):
    df = pd.read_csv(csv_path)
    df["price"].fillna(df["price"].median(), inplace=True)
    df["quantity_sold"].fillna(df["quantity_sold"].median(), inplace=True)
    df["rating"] = df.groupby("category")["rating"].transform(lambda x: x.fillna(x.mean()))

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["review_count"].fillna(0, inplace=True)

    return df


def modify_already_existing_data(product_instance):
    try:
        product_id = product_instance.product_id
        existing_product_obj = Product.objects.filter(product_id=product_id)
        if existing_product_obj:
            existing_product_obj = existing_product_obj[0]
            if product_instance.product_name.lower() == existing_product_obj.product_name.lower() and \
                product_instance.category.lower() == existing_product_obj.category.lower():

                new_review_count = existing_product_obj.review_count + product_instance.review_count
                new_quantity_sold = existing_product_obj.quantity_sold + product_instance.quantity_sold
                new_rating = (
                    (existing_product_obj.rating  * existing_product_obj.quantity_sold) + 
                    (product_instance.rating * product_instance.quantity_sold) / new_quantity_sold
                )

                new_price = (
                    (existing_product_obj.price  * existing_product_obj.quantity_sold) + 
                    (product_instance.price * product_instance.quantity_sold) / new_quantity_sold
                )

                existing_product_obj.price = new_price
                existing_product_obj.rating = new_rating
                existing_product_obj.review_count = new_review_count
                existing_product_obj.quantity_sold = product_instance.quantity_sold
                existing_product_obj.save()

    except Exception as e:
        print(e)


def create_table_instances(table, table_dataframe):
    table_instances = []
    for _, row in table_dataframe.iterrows():
        a_table_instance = table(**row)
        table_instances.append(a_table_instance)
    return table_instances


def upload_data_in_batches(table, table_instances, batch_size):
    for bacth_start in range(0, len(table_instances), batch_size):
        try:
            table.objects.bulk_create(table_instances[bacth_start:bacth_start + batch_size])
        except Exception as e:
            for a_instance_index in range(bacth_start, bacth_start+batch_size):
                try:
                    table_instances[a_instance_index].save()
                except IntegrityError:
                    modify_already_existing_data(table_instances[a_instance_index])
                except IndexError:
                    break
                except Exception as e:
                    print(e)


def upload_data(data):
    product_instances = create_table_instances(Product, data)
    batch_size = constants.BULK_CREATE_BATCH_SIZE
    upload_data_in_batches(Product, product_instances, batch_size)
