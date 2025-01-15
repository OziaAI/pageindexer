import shopify
from sentence_transformers import SentenceTransformer


def create_product_document(model: SentenceTransformer, product: shopify.Product):
    product_options_values = [option.values for option in product.attributes["options"]]

    product_options = sum(product_options_values, [])

    product_options = [
        option for option in product_options if option.lower() != "default title"
    ]

    title = product.attributes["title"].lower()
    description = product.attributes["body_html"]
    embedding = model.encode(title + " - " + description, show_progress_bar=False)

    document = {
        "title": title,
        "description": description,
        "vendor": product.attributes["vendor"].upper(),
        "image_link": product.attributes["image"].src,
        "options": product_options,
        "vector": embedding,
    }

    print("Indexer - Created following document:")
    print(document)

    return document
