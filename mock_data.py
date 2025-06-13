from typing import List, Dict, Any

"""Mock data for testing the MCP server"""

MOCK_PRODUCTS = [
    {
        "id": "1",
        "name": "iPhone 15 Pro",
        "description": "Latest iPhone with A17 Pro chip",
        "price": 999.99,
        "category": "Phones",
        "brand": "Apple",
        "in_stock": True,
        "specifications": {
            "processor": "A17 Pro",
            "ram": "8GB",
            "storage": "256GB",
            "display": "6.1 inch Super Retina XDR"
        }
    },
    {
        "id": "2",
        "name": "Samsung Galaxy S24",
        "description": "Latest Samsung flagship with AI features",
        "price": 899.99,
        "category": "Phones",
        "brand": "Samsung",
        "in_stock": True,
        "specifications": {
            "processor": "Snapdragon 8 Gen 3",
            "ram": "12GB",
            "storage": "512GB",
            "display": "6.2 inch Dynamic AMOLED"
        }
    }
]

MOCK_CATEGORIES = [
    {
        "id": "1",
        "name": "Phones",
        "description": "Smartphones and mobile devices"
    },
    {
        "id": "2",
        "name": "Laptops",
        "description": "Portable computers and accessories"
    }
]

MOCK_BRANDS = [
    {
        "id": "1",
        "name": "Apple",
        "description": "Technology company known for iPhone and Mac"
    },
    {
        "id": "2",
        "name": "Samsung",
        "description": "Electronics manufacturer"
    }
]

MOCK_GRAPHQL_RESPONSES = [
    {
        "data": {
            "products": MOCK_PRODUCTS,
            "categories": MOCK_CATEGORIES,
            "brands": MOCK_BRANDS
        }
    }
]

MOCK_REST_RESPONSES = [
    {
        "data": MOCK_PRODUCTS,
        "meta": {
            "total": len(MOCK_PRODUCTS),
            "page": 1,
            "per_page": 10
        }
    }
] 