from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
from dotenv import load_dotenv
import urllib.parse
import json
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import base64

# Load environment variables
load_dotenv()

# Debug: Print environment variables to check if they're loaded
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="بروزرسان قفسه‌های بسلام")

# Mount static files with cache headers
from starlette.staticfiles import StaticFiles
from starlette.responses import Response

class CachedStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # Add cache headers for static files
            response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
            response.headers["ETag"] = f'"{hash(path)}"'
        return response

app.mount("/static", CachedStaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Basalam API configuration
BASALAM_CLIENT_ID = os.getenv("BASALAM_CLIENT_ID")
BASALAM_CLIENT_SECRET = os.getenv("BASALAM_CLIENT_SECRET")
BASALAM_REDIRECT_URI = os.getenv("BASALAM_REDIRECT_URI")
BASALAM_SCOPE = os.getenv("BASALAM_SCOPE", "vendor.profile.read vendor.product.read vendor.product.write customer.profile.read")

# Debug: Log the environment variables
logger.info(f"BASALAM_CLIENT_ID: {BASALAM_CLIENT_ID}")
logger.info(f"BASALAM_REDIRECT_URI: {BASALAM_REDIRECT_URI}")
logger.info(f"BASALAM_SCOPE: {BASALAM_SCOPE}")

# Validate required environment variables
if not BASALAM_CLIENT_ID:
    raise ValueError("BASALAM_CLIENT_ID environment variable is required")
if not BASALAM_CLIENT_SECRET:
    raise ValueError("BASALAM_CLIENT_SECRET environment variable is required")

# Correct Basalam OAuth endpoints
BASALAM_AUTH_URL = "https://basalam.com/accounts/sso"
BASALAM_TOKEN_URL = "https://auth.basalam.com/oauth/token"
BASALAM_API_BASE = "https://core.basalam.com"

# Store tokens and state temporarily (in production, use proper storage)
user_tokens = {}
user_states = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with authentication"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth/login")
async def login():
    """Redirect to Basalam OAuth"""
    import secrets
    import uuid

    # Generate unique session ID and state for security
    session_id = str(uuid.uuid4())
    state = secrets.token_urlsafe(24)

    # Store state with session ID for tracking
    user_states[session_id] = {
        "state": state,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Normalize scope to ensure proper space separation (no plus signs)
    scope = BASALAM_SCOPE.replace(",", " ").replace("+", " ").strip()

    params = {
        "client_id": BASALAM_CLIENT_ID,
        "scope": scope,
        "redirect_uri": BASALAM_REDIRECT_URI,
        "state": f"{session_id}:{state}"  # Include session ID in state
    }

    # Use correct Basalam OAuth URL with spaces in scope
    auth_url = f"{BASALAM_AUTH_URL}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
    logger.info(f"Generated OAuth URL: {auth_url}")
    logger.info(f"Session ID: {session_id}, State: {state}")

    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle OAuth callback"""
    logger.info(f"OAuth callback received - Code length: {len(code) if code else 0}, State: {state}")

    if error:
        logger.error(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"Authentication error: {error}")

    if not code:
        logger.error("No authorization code received")
        raise HTTPException(status_code=400, detail="No authorization code received")

    # Parse state parameter (format: session_id:state for new format, or just state for old format)
    if not state:
        logger.error("No state parameter received")
        raise HTTPException(status_code=400, detail="No state parameter received")

    # Handle both new format (session_id:state) and old format (just state)
    if ":" in state:
        # New format with session ID
        session_id, received_state = state.split(":", 1)
        expected_data = user_states.get(session_id)
        if not expected_data:
            logger.error(f"Session not found: {session_id}")
            raise HTTPException(status_code=400, detail="Session not found")
        expected_state = expected_data["state"]
    else:
        # Old format - check all stored states
        received_state = state
        expected_state = None
        for session_data in user_states.values():
            if session_data["state"] == received_state:
                expected_state = received_state
                break

        if not expected_state:
            logger.error(f"State not found in any session: {received_state}")
            raise HTTPException(status_code=400, detail="Invalid state parameter")

    if received_state != expected_state:
        logger.error(f"State mismatch - Expected: {expected_state}, Received: {received_state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    logger.info("State validation successful")

    # Exchange code for token using correct method
    async with httpx.AsyncClient(timeout=30) as client:
        token_url = BASALAM_TOKEN_URL
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": BASALAM_CLIENT_ID,
            "client_secret": BASALAM_CLIENT_SECRET,
            "redirect_uri": BASALAM_REDIRECT_URI,
        }

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        logger.info(f"Sending token exchange request to: {token_url}")
        response = await client.post(token_url, json=payload, headers=headers)

        logger.info(f"Token exchange response status: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(status_code=400, detail=f"Failed to get access token: {response.text}")

        token_info = response.json()
        access_token = token_info.get("access_token")

        if not access_token:
            logger.error(f"No access token in response: {token_info}")
            raise HTTPException(status_code=400, detail="No access token in response")

        # Store token (in production, use proper storage with user sessions)
        user_tokens["current_user"] = access_token

        # Clean up state after successful authentication
        if ":" in state:
            # New format with session ID
            session_id, _ = state.split(":", 1)
            if session_id in user_states:
                del user_states[session_id]
        else:
            # Old format - find and remove the state from any session
            for session_id, session_data in list(user_states.items()):
                if session_data["state"] == received_state:
                    del user_states[session_id]
                    break

        logger.info("OAuth authentication successful - Token obtained and stored")
        return RedirectResponse("/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard showing shelves and products"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/user/me")
async def get_user_info():
    """Get current user information"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        response = await client.get(f"{BASALAM_API_BASE}/v3/users/me", headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get user info")

        user_data = response.json()
        logger.info(f"📋 User info API called - Vendor ID: {user_data.get('vendor', {}).get('id')}")
        return user_data

@app.get("/api/debug/user-info")
async def debug_user_info():
    """Debug endpoint to see raw user info structure"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        response = await client.get(f"{BASALAM_API_BASE}/v3/users/me", headers=headers)

        if response.status_code != 200:
            return {
                "error": "Failed to get user info",
                "status_code": response.status_code,
                "response_text": response.text
            }

        user_data = response.json()
        return {
            "user_id": user_data.get("id"),
            "user_name": user_data.get("name"),
            "vendor_object": user_data.get("vendor", {}),
            "vendor_id": user_data.get("vendor", {}).get("id"),
            "vendor_title": user_data.get("vendor", {}).get("title"),
            "full_response": user_data
        }

@app.get("/api/shelves")
async def get_user_shelves():
    """Get user shelves using vendor ID"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        # First get user info to get vendor ID
        logger.info("🔍 Fetching user info from /v3/users/me to get vendor ID")
        user_response = await client.get(f"{BASALAM_API_BASE}/v3/users/me", headers=headers)
        if user_response.status_code != 200:
            logger.error(f"❌ Failed to get user info: {user_response.status_code} - {user_response.text}")
            raise HTTPException(status_code=user_response.status_code, detail="Failed to get user info")

        user_data = user_response.json()
        logger.info(f"✅ User data received: {user_data}")

        # Extract vendor ID safely with detailed error handling
        vendor = user_data.get("vendor", {})
        vendor_id = vendor.get("id") if vendor else None

        logger.info(f"📋 Vendor object: {vendor}")
        logger.info(f"🎯 Extracted vendor ID: {vendor_id}")
        logger.info(f"👤 User ID (for comparison): {user_data.get('id')}")
        logger.info(f"📊 Vendor ID type: {type(vendor_id)}")

        # Additional debugging for vendor object structure
        if isinstance(vendor, dict):
            logger.info(f"📋 Vendor keys: {list(vendor.keys())}")
            for key, value in vendor.items():
                logger.info(f"   {key}: {value} (type: {type(value)})")

        if not vendor_id:
            logger.error(f"❌ No vendor ID found in user data")
            logger.error(f"   Vendor object: {vendor}")
            logger.error(f"   Vendor object type: {type(vendor)}")
            logger.error(f"   Full user data keys: {list(user_data.keys())}")
            logger.error(f"   User ID: {user_data.get('id')}")

            # Try fallback: use user ID if vendor ID is missing (for debugging)
            user_id = user_data.get("id")
            logger.warning(f"⚠️ Trying fallback with user ID: {user_id}")

            # For debugging, let's try the user ID first to see what error we get
            fallback_url = f"{BASALAM_API_BASE}/api_v2/shelve/list/{user_id}"
            logger.info(f"🧪 Testing fallback with user ID: {fallback_url}")

            fallback_response = await client.get(fallback_url, headers=headers)
            logger.info(f"🧪 Fallback response status: {fallback_response.status_code}")

            if fallback_response.status_code == 200:
                logger.info("✅ Fallback with user ID worked! This suggests the issue is with vendor ID extraction")
                logger.info("📝 The user might not have vendor privileges, or the vendor ID field structure is different")
                # Return the fallback result for now
                return fallback_response.json()
            else:
                logger.info(f"❌ Fallback also failed: {fallback_response.text}")

            raise HTTPException(
                status_code=400,
                detail="Could not get vendor ID from user info. " +
                      f"Vendor object: {vendor}. " +
                      f"Available user data keys: {list(user_data.keys())}. " +
                      f"User ID: {user_id}. " +
                      f"Fallback test status: {fallback_response.status_code}"
            )

        # Verify we're using vendor ID, not user ID
        user_id = user_data.get("id")
        if vendor_id == user_id:
            logger.warning("⚠️ Vendor ID equals User ID - this might be the issue!")

        logger.info(f"🔄 Using vendor ID: {vendor_id} for shelves API (NOT user ID: {user_id})")

        # Get shelves using vendor ID
        shelves_url = f"{BASALAM_API_BASE}/api_v2/shelve/list/{vendor_id}"
        logger.info(f"📡 Requesting shelves from: {shelves_url}")

        shelves_response = await client.get(shelves_url, headers=headers)
        logger.info(f"📥 Shelves API response status: {shelves_response.status_code}")

        if shelves_response.status_code != 200:
            logger.error(f"❌ Failed to get shelves: {shelves_response.status_code} - {shelves_response.text}")
            raise HTTPException(status_code=shelves_response.status_code, detail=f"Failed to get shelves: {shelves_response.text}")

        shelves_data = shelves_response.json()
        logger.info(f"✅ Shelves data received successfully: {len(shelves_data) if isinstance(shelves_data, list) else 'N/A'} items")
        return shelves_data

@app.get("/api/shelves/{shelf_id}/products")
async def get_shelf_products(shelf_id: int):
    """Get products for a specific shelf"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        response = await client.get(f"{BASALAM_API_BASE}/api_v2/shelve/{shelf_id}/products", headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get shelf products")

        products_data = response.json()

        # Debug: Log the raw API response structure
        # Ensure consistent response structure
        if isinstance(products_data, dict) and 'data' in products_data:
            return products_data['data']
        elif isinstance(products_data, list):
            return products_data
        else:
            # If it's some other structure, return as is
            logger.warning(f"Unexpected products data structure: {type(products_data)}")
            return products_data

@app.get("/api/debug/shelf/{shelf_id}/products")
async def debug_shelf_products(shelf_id: int):
    """Debug endpoint to see raw API response structure"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        response = await client.get(f"{BASALAM_API_BASE}/api_v2/shelve/{shelf_id}/products", headers=headers)

        if response.status_code != 200:
            return {
                "error": "Failed to get shelf products",
                "status_code": response.status_code,
                "response_text": response.text
            }

        products_data = response.json()

        # Process the response the same way as the main endpoint
        processed_data = products_data
        if isinstance(products_data, dict) and 'data' in products_data:
            processed_data = products_data['data']
        elif isinstance(products_data, list):
            processed_data = products_data

        return {
            "raw_response": products_data,
            "processed_response": processed_data,
            "response_type": type(products_data).__name__,
            "length": len(products_data) if hasattr(products_data, '__len__') else None,
            "first_product": processed_data[0] if isinstance(processed_data, list) and len(processed_data) > 0 else None,
            "photo_structure": processed_data[0]['photo'] if isinstance(processed_data, list) and len(processed_data) > 0 and isinstance(processed_data[0], dict) and 'photo' in processed_data[0] else None
        }

@app.post("/api/shelves/{shelf_id}/update-descriptions")
async def update_shelf_descriptions(shelf_id: int, description: str = Form(...)):
    """Update descriptions for all products in a shelf"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # First get all products in the shelf
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        products_response = await client.get(f"{BASALAM_API_BASE}/api_v2/shelve/{shelf_id}/products", headers=headers)
        
        if products_response.status_code != 200:
            raise HTTPException(status_code=products_response.status_code, detail="Failed to get shelf products")
        
        products_data = products_response.json()
        products = products_data.get("data", []) if isinstance(products_data, dict) else products_data
        
        updated_products = []
        failed_products = []
        
        # Update each product
        for product in products:
            product_id = product.get("id")
            if not product_id:
                continue
                
            update_data = {
                "description": description
            }
            
            # Create specific headers for the update request
            update_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            update_response = await client.patch(
                f"{BASALAM_API_BASE}/v4/products/{product_id}",
                headers=update_headers,
                json=update_data
                )

                # Validate that the update actually worked by checking the response
            if update_response.status_code == 200:
                try:
                    response_data = update_response.json()
                    logger.info(f"Description updated successfully for product {product_id}")
                except:
                    logger.warning(f"Product {product_id} updated but response not parseable")
            else:
                logger.error(f"Failed to update product {product_id}: {update_response.status_code}")
            
            if update_response.status_code == 200:
                updated_products.append(product)
            else:
                failed_products.append({
                    "product": product,
                    "error": update_response.text
                })
        
        return {
            "success": True,
            "updated_count": len(updated_products),
            "failed_count": len(failed_products),
            "updated_products": updated_products,
            "failed_products": failed_products
        }

@app.post("/api/shelves/{shelf_id}/update-images")
async def update_shelf_images(request: Request, shelf_id: int):
    """Update images for all products in a shelf"""
    token = user_tokens.get("current_user")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    form = await request.form()
    image_file = form.get("image")

    if not image_file:
        raise HTTPException(status_code=400, detail="No image file provided")

    # First get all products in the shelf
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        products_response = await client.get(f"{BASALAM_API_BASE}/api_v2/shelve/{shelf_id}/products", headers=headers)
        
        if products_response.status_code != 200:
            raise HTTPException(status_code=products_response.status_code, detail="Failed to get shelf products")
        
        products_data = products_response.json()
        products = products_data.get("data", []) if isinstance(products_data, dict) else products_data
        
        updated_products = []
        failed_products = []
        
        # Read image content
        image_content = await image_file.read()
        
        # Update each product
        for product in products:
            product_id = product.get("id")
            if not product_id:
                continue
            
            # Try different approaches for image upload

            # Method 1: JSON with base64 encoded image
            try:
                # Encode image to base64
                image_base64 = base64.b64encode(image_content).decode('utf-8')

                # Prepare JSON payload
                image_data = {
                    "image": f"data:{image_file.content_type};base64,{image_base64}",
                    "filename": image_file.filename
                }

                upload_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }

                # Try different upload methods silently, only log success/failure
                methods_tried = []

                # Method 1: Simple image field
                update_response = await client.patch(
                    f"{BASALAM_API_BASE}/v4/products/{product_id}",
                    headers=upload_headers,
                    json=image_data
                )
                methods_tried.append(("Method 1", update_response.status_code))

                # Method 2: Photo object structure (if Method 1 fails)
                if update_response.status_code != 200:
                    image_data_alt = {
                        "photo": {
                            "data": f"data:{image_file.content_type};base64,{image_base64}",
                            "filename": image_file.filename
                        }
                    }

                    update_response = await client.patch(
                        f"{BASALAM_API_BASE}/v4/products/{product_id}",
                        headers=upload_headers,
                        json=image_data_alt
                    )
                    methods_tried.append(("Method 2", update_response.status_code))

                # Method 3: Multipart form data (if Method 2 fails)
                if update_response.status_code != 200:
                    files = {
                        "image": (image_file.filename, image_content, image_file.content_type)
                    }

                    multipart_headers = {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    }

                    update_response = await client.patch(
                        f"{BASALAM_API_BASE}/v4/products/{product_id}",
                        headers=multipart_headers,
                        files=files
                    )
                    methods_tried.append(("Method 3", update_response.status_code))

                # Log the result
                if update_response.status_code == 200:
                    successful_method = methods_tried[-1][0] if methods_tried else "Unknown"
                    logger.info(f"Image uploaded successfully for product {product_id} using {successful_method}")

                    # Verify the image was actually updated by checking the response
                    try:
                        response_data = update_response.json()
                        if 'photo' in response_data or 'image' in response_data:
                            logger.info(f"Image update verified for product {product_id}")
                        else:
                            logger.warning(f"Image upload may not have been processed correctly for product {product_id}")
                    except:
                        logger.info(f"Image uploaded for product {product_id} (response format unclear)")
                else:
                    logger.error(f"Image upload failed for product {product_id}: {update_response.text}")

            except Exception as upload_error:
                logger.error(f"Error during image upload for product {product_id}: {upload_error}")
                update_response = type('Response', (), {'status_code': 500, 'text': str(upload_error)})()

            # Clean up the logging - only show essential info
            
            if update_response.status_code == 200:
                updated_products.append(product)
            else:
                failed_products.append({
                    "product": product,
                    "error": update_response.text
                })
        
        return {
            "success": True,
            "updated_count": len(updated_products),
            "failed_count": len(failed_products),
            "updated_products": updated_products,
            "failed_products": failed_products
        }

@app.get("/api/auth/status")
async def auth_status():
    """Check authentication status"""
    token = user_tokens.get("current_user")
    return {"authenticated": bool(token)}

@app.get("/api/debug/token")
async def debug_token():
    """Debug endpoint to check token status"""
    token = user_tokens.get("current_user")
    return {
        "has_token": bool(token),
        "token_length": len(token) if token else 0,
        "token_prefix": token[:50] + "..." if token and len(token) > 50 else token,
        "all_tokens_count": len(user_tokens)
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "server_time": datetime.utcnow().isoformat(),
        "authenticated_users": len([t for t in user_tokens.values() if t]),
        "static_files_cached": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
