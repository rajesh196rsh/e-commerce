from django.db.utils import IntegrityError
from typing import Type, List
from django.db.models import Model
import pandas as pd
from .models import Product
from . import constants


def extract_and_clean_product_data(csv_path: str) -> pd.DataFrame:
    """
    Extracts and cleans product data from a CSV file.

    This function performs the following operations:
        - Reads the CSV file into a DataFrame.
        - Fills missing values in the 'price' and 'quantity_sold' columns with their respective medians.
        - Fills missing values in the 'rating' column with the mean rating for each category.
        - Converts 'price', 'quantity_sold', and 'rating' columns to numeric types, coercing errors.
        - Fills missing values in the 'review_count' column with 0.

    Args:
        csv_path (str): The file path to the CSV file containing product data.

    Returns:
        pd.DataFrame: A cleaned DataFrame with the following columns:
            - 'price': The price of the product (numeric).
            - 'quantity_sold': The quantity of the product sold (numeric).
            - 'rating': The rating of the product, with missing values filled per category mean (numeric).
            - 'review_count': The number of reviews for the product, with missing values filled with 0.
    """

    df = pd.read_csv(csv_path)

    # Filling missing values
    df["price"].fillna(df["price"].median(), inplace=True)
    df["quantity_sold"].fillna(df["quantity_sold"].median(), inplace=True)
    df["rating"] = df.groupby("category")["rating"].transform(lambda x: x.fillna(x.mean()))

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Filling review count with 0 if not present
    df["review_count"].fillna(0, inplace=True)

    return df


def modify_already_existing_data(product_instance: Type[Model]) -> None:
    """
    Modifies an existing product record in the database with new data from the provided product instance.

    This function performs the following operations:
        - Fetches an existing product record based on the `product_id` from the provided `product_instance`.
        - If an existing product record is found and both the product name and category match (case-insensitive),
          it updates the following attributes:
            - `price`: A weighted average price based on the quantity sold.
            - `rating`: A weighted average rating based on the quantity sold.
            - `review_count`: The total number of reviews, summing up the existing and new review counts.
            - `quantity_sold`: The updated quantity sold for the existing product.
        - Saves the updated product record back to the database.

    Args:
        product_instance (Type[models.Model]): An instance of a product model containing new data to be merged with
            the existing product record. The instance should have at least the following attributes:
            - `product_id`: The unique identifier for the product.
            - `product_name`: The name of the product.
            - `category`: The category of the product.
            - `price`: The price of the product.
            - `rating`: The rating of the product.
            - `review_count`: The number of reviews for the product.
            - `quantity_sold`: The quantity of the product sold.

    Returns:
        None: This function does not return any value.
    """
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


def create_table_instances(table: Type[Model], table_dataframe: pd.DataFrame) -> List[Model]:
    """
    Creates a list of model instances from a DataFrame.

    This function takes a Django model class and a DataFrame, and creates instances of the model 
    based on the data in the DataFrame. Each row in the DataFrame is used to create an instance of the model.

    Args:
        table (Type[Model]): The Django model class to create instances of. It should be a subclass of `django.db.models.Model`.
        table_dataframe (pd.DataFrame): A DataFrame where each row represents the fields and values for a model instance.
            The DataFrame's columns should match the model's fields.

    Returns:
        List[Model]: A list of instances of the model, created based on the rows in the DataFrame.
    """
    table_instances = []
    for _, row in table_dataframe.iterrows():
        a_table_instance = table(**row)
        table_instances.append(a_table_instance)
    return table_instances


def upload_data_in_batches(table: Type[Model], table_instances: List[Model], batch_size: int) -> None:
    """
    Uploads a list of model instances to the database in batches.

    This function inserts model instances into the database in batches. If an error occurs during bulk creation,
    it attempts to handle individual instances that failed to be created by saving them individually. If an
    `IntegrityError` occurs, it tries to modify the existing data.

    Args:
        table (Type[Model]): The Django model class used to create and upload instances. It should be a subclass of `django.db.models.Model`.
        table_instances (List[Model]): A list of model instances to be uploaded to the database.
        batch_size (int): The number of instances to include in each batch during the upload process.

    Returns:
        None: This function does not return any value.
    """
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


def upload_data(data: pd.DataFrame) -> None:
    """
    Converts a DataFrame to model instances and uploads them to the database in batches.

    This function processes a DataFrame, creates model instances from its rows, and uploads these instances
    to the database in batches. It utilizes the `create_table_instances` function to create instances and
    the `upload_data_in_batches` function to handle batch uploads.

    Args:
        data (pd.DataFrame): A DataFrame where each row represents the fields and values for a model instance.
            The DataFrame's columns should match the model's fields.

    Returns:
        None: This function does not return any value.
    """
    product_instances = create_table_instances(Product, data)
    batch_size = constants.BULK_CREATE_BATCH_SIZE
    upload_data_in_batches(Product, product_instances, batch_size)
