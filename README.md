# Basalam Shelves Updater

A modern web application for managing Basalam shelves and bulk updating product information.

## Features

- 🔐 **Secure OAuth Authentication** with Basalam
- 📦 **Shelf Management** - View all your shelves and products
- ✏️ **Bulk Description Updates** - Update descriptions for all products in a shelf
- 🖼️ **Bulk Image Updates** - Update images for all products in a shelf
- 📊 **Update Review** - See detailed results of your changes
- 🎨 **Modern UI** - Beautiful, responsive, and user-friendly interface

## Prerequisites

- Python 3.8+
- Basalam Developer Account
- Valid Basalam API credentials

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd basalam-shelves-updater
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory with your Basalam credentials:
   ```env
   BASALAM_CLIENT_ID=your_client_id
   BASALAM_CLIENT_SECRET=your_client_secret
   APP_NAME=Basalam Shelves Updater
   BASALAM_REDIRECT_URI=http://myapp.test:8000/auth/callback
   BASALAM_SCOPE=vendor.profile.read vendor.product.read customer.profile.read
   ```

4. **Configure your hosts file (optional)**
   Add this line to your hosts file for the redirect URI to work:
   ```
   127.0.0.1 myapp.test
   ```

## Usage

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Access the application**
   Open your browser and go to `http://myapp.test:8000` or `http://localhost:8000`

3. **Authenticate**
   Click "Login with Basalam" to authenticate with your Basalam account

4. **Manage your shelves**
   - View all your shelves and their products
   - Click "Update All" on any shelf to bulk update products
   - Choose between updating descriptions or images
   - Review the results after each update

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET /auth/login` - Initiate OAuth login with Basalam SSO
- `GET /auth/callback` - OAuth callback handler (receives code and state)
- `GET /api/auth/status` - Check authentication status

### Dashboard
- `GET /dashboard` - Dashboard page
- `GET /api/user/me` - Get current user information from `/v3/users/me`
- `GET /api/shelves` - Get user shelves using vendor ID (from user info)
- `GET /api/shelves/{shelf_id}/products` - Get products for a shelf

### Updates
- `POST /api/shelves/{shelf_id}/update-descriptions` - Update descriptions for all products in a shelf
- `POST /api/shelves/{shelf_id}/update-images` - Update images for all products in a shelf

## Project Structure

```
basalam-shelves-updater/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   └── dashboard.html     # Dashboard page
└── static/                # Static files
    ├── style.css          # Custom CSS
    └── app.js             # Frontend JavaScript
```

## Technology Stack

- **Backend**: FastAPI, Python, httpx for async HTTP requests
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: OAuth 2.0 with Basalam SSO
- **API Integration**: Basalam REST API (core.basalam.com, auth.basalam.com)
- **Styling**: Modern CSS with gradients and RTL support for Persian

## Troubleshooting

### Common Issues

1. **Authentication fails**
   - Check your Basalam credentials in `.env`
   - Ensure the redirect URI matches your Basalam app settings
   - Make sure your hosts file is configured correctly

2. **Can't load shelves**
   - Verify your OAuth scopes include the required permissions
   - Check that your Basalam account has access to the vendor APIs

3. **Updates fail**
   - Ensure you have the necessary permissions for your products
   - Check the Basalam API documentation for any changes

### Support

For issues with the Basalam API, consult the official documentation:
- [Basalam Developers](https://developers.basalam.com/)
- [Quick Start Guide](https://developers.basalam.com/quick-start)
- [API Reference](https://developers.basalam.com/rest/core)

## License

This project is for educational and development purposes. Please ensure compliance with Basalam's terms of service.
