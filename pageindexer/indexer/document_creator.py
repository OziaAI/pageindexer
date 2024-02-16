import shopify

def create_product_document(product: shopify.Product):
    product_options_values = [ option.values for option in product.attributes["options"]]

    product_options = sum(product_options_values, [])

    product_options = [option for option in product_options 
                       if option.lower() != "default title"]

    document = {
        "title": product.attributes["title"].lower(),
        "description": product.attributes["body_html"],
        "vendor": product.attributes["vendor"].upper(),
        "image_link": product.attributes["image"].src,
        "options": product_options
    }

    print("Indexer - Created following document:")
    print(document)

    return document
