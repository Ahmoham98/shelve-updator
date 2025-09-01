#!/usr/bin/env python3
"""
Verify if image uploads are actually working by checking product data before/after
"""

import httpx
import asyncio
import json

async def verify_image_update():
    """Verify if images are actually being updated"""

    print("🔍 VERIFYING IMAGE UPDATE FUNCTIONALITY")
    print("=" * 50)

    base_url = "http://127.0.0.1:8000"

    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{base_url}/api/health")
            if response.status_code != 200:
                print("❌ Server not running")
                return
            print("✅ Server is running")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return

    # Check if user is authenticated
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/auth/status")
            auth_data = response.json()
            if not auth_data.get('authenticated'):
                print("❌ User not authenticated")
                return
            print("✅ User is authenticated")
    except Exception as e:
        print(f"❌ Cannot check auth: {e}")
        return

    # Get shelves to find one with products
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/shelves")
            if response.status_code == 200:
                shelves = response.json()
                if shelves and len(shelves) > 0:
                    shelf_id = shelves[0]['id']
                    print(f"Testing with shelf: {shelf_id}")

                    # Get products for the shelf
                    products_response = await client.get(f"{base_url}/api/shelves/{shelf_id}/products")
                    if products_response.status_code == 200:
                        products = products_response.json()
                        print(f"Found {len(products)} products")

                        if len(products) > 0:
                            first_product = products[0]
                            product_id = first_product.get('id')
                            current_photo = first_product.get('photo', {})

                            print(f"Product ID: {product_id}")
                            print("Current photo structure:")
                            print(f"  Extra small: {current_photo.get('extra_small', 'None')[:50]}...")
                            print(f"  Small: {current_photo.get('small', 'None')[:50]}...")
                            print(f"  Medium: {current_photo.get('medium', 'None')[:50]}...")
                            print(f"  Large: {current_photo.get('large', 'None')[:50]}...")

                            print("\n📋 RECOMMENDATIONS:")
                            print("1. Try uploading a small test image (under 1MB)")
                            print("2. Check if the image file format is supported by Basalam")
                            print("3. Verify that you have the correct permissions for the vendor")
                            print("4. Check if Basalam has any image processing delays")
                            print("5. Try refreshing the Basalam dashboard after a few minutes")

                            print("\n🔍 If images still don't update:")
                            print("- The API might be accepting the upload but not processing it")
                            print("- There might be vendor permission restrictions")
                            print("- Basalam might have image moderation/processing delays")
                            print("- Check Basalam's API documentation for image upload requirements")

                        else:
                            print("❌ No products found in shelf")
                    else:
                        print(f"❌ Cannot get products: {products_response.status_code}")
                else:
                    print("❌ No shelves found")
            else:
                print(f"❌ Cannot get shelves: {response.status_code}")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    asyncio.run(verify_image_update())
