// Basalam Shelves Updater - Frontend JavaScript

class BasalamApp {
    constructor() {
        this.currentShelfId = null;
        this.userInfo = null;
        this.shelves = [];
        this.init();
    }

    init() {
        this.checkAuthStatus();
        this.setupEventListeners();
        
        // Load data if on dashboard
        if (window.location.pathname === '/dashboard') {
            this.loadDashboardData();
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            const authSection = document.getElementById('auth-section');
            const authStatus = document.getElementById('auth-status');
            
            if (data.authenticated) {
                if (authSection) {
                    authSection.innerHTML = `
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle ms-2"></i>
                            شما با موفقیت احراز هویت شده‌اید!
                        </div>
                        <a href="/dashboard" class="btn btn-primary btn-lg">
                            <i class="fas fa-tachometer-alt ms-2"></i>
                            رفتن به داشبورد
                        </a>
                    `;
                }
                if (authStatus) {
                    authStatus.innerHTML = `
                        <span class="navbar-text text-light">
                            <i class="fas fa-user-check ms-1"></i>
                            احراز هویت شده
                        </span>
                    `;
                }
            } else {
                if (authSection) {
                    authSection.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle ms-2"></i>
                            لطفاً برای ادامه با حساب بسلام خود احراز هویت کنید.
                        </div>
                        <a href="/auth/login" class="btn btn-primary btn-lg">
                            <i class="fas fa-sign-in-alt ms-2"></i>
                            ورود با بسلام
                        </a>
                    `;
                }
                if (authStatus) {
                    authStatus.innerHTML = `
                        <a href="/auth/login" class="btn btn-outline-light btn-sm">
                            <i class="fas fa-sign-in-alt ms-1"></i>
                            ورود
                        </a>
                    `;
                }
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
        }
    }

    setupEventListeners() {
        // Update forms
        const descForm = document.getElementById('updateDescriptionForm');
        const imageForm = document.getElementById('updateImageForm');
        
        if (descForm) {
            descForm.addEventListener('submit', (e) => this.handleDescriptionUpdate(e));
        }
        
        if (imageForm) {
            imageForm.addEventListener('submit', (e) => this.handleImageUpdate(e));
        }
    }

    async loadDashboardData() {
        await this.loadUserInfo();
        await this.loadShelves();
    }

    async loadUserInfo() {
        try {
            const response = await fetch('/api/user/me');
            if (!response.ok) {
                throw new Error('Failed to load user info');
            }
            
            this.userInfo = await response.json();
            this.displayUserInfo();
        } catch (error) {
            console.error('Error loading user info:', error);
            document.getElementById('user-info').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle ms-2"></i>
                    بارگذاری اطلاعات کاربر ناموفق بود. لطفاً صفحه را بروزرسانی کنید.
                </div>
            `;
        }
    }

    displayUserInfo() {
        const userInfoEl = document.getElementById('user-info');
        if (this.userInfo && userInfoEl) {
            userInfoEl.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <strong>نام:</strong> ${this.userInfo.name || this.userInfo.first_name || 'موجود نیست'}
                    </div>
                    <div class="col-md-6">
                        <strong>شناسه:</strong> ${this.userInfo.id || this.userInfo.user_id || 'موجود نیست'}
                    </div>
                </div>
            `;
        }
    }

    async loadShelves() {
        try {
            const response = await fetch('/api/shelves');
            if (!response.ok) {
                throw new Error('Failed to load shelves');
            }
            
            const shelvesData = await response.json();
            this.shelves = shelvesData.data || shelvesData || [];
            this.displayShelves();
        } catch (error) {
            console.error('Error loading shelves:', error);
            document.getElementById('shelves-container').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load shelves. Please try refreshing the page.
                </div>
            `;
        }
    }

    async displayShelves() {
        const container = document.getElementById('shelves-container');
        
        if (!this.shelves || this.shelves.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4">
                    <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">هیچ قفسه‌ای یافت نشد</h5>
                    <p>شما هنوز هیچ قفسه‌ای ندارید.</p>
                </div>
            `;
            return;
        }

        let shelvesHtml = '';
        
        for (const shelf of this.shelves) {
            const products = await this.loadShelfProducts(shelf.id);
            shelvesHtml += this.createShelfCard(shelf, products);
        }
        
        container.innerHTML = shelvesHtml;

        // Debug: Check what's actually in the DOM after insertion
        setTimeout(() => {
            const shelfCards = container.querySelectorAll('.shelf-card');
            const productGrids = container.querySelectorAll('.product-grid');
            const allImages = container.querySelectorAll('img');
            const allPlaceholders = container.querySelectorAll('.product-image-placeholder');

            console.log('DOM Inspection after HTML insertion:', {
                shelfCards: shelfCards.length,
                productGrids: productGrids.length,
                totalImages: allImages.length,
                totalPlaceholders: allPlaceholders.length,
                containerHTML: container.innerHTML.substring(0, 500) + '...'
            });

            if (allImages.length > 0) {
                console.log('First image in DOM:', {
                    src: allImages[0].src,
                    alt: allImages[0].alt,
                    naturalWidth: allImages[0].naturalWidth,
                    naturalHeight: allImages[0].naturalHeight,
                    complete: allImages[0].complete,
                    currentSrc: allImages[0].currentSrc
                });

                // Add load/error event listeners to the first image
                allImages[0].addEventListener('load', () => console.log('Image loaded successfully:', allImages[0].src));
                allImages[0].addEventListener('error', (e) => console.error('Image failed to load:', allImages[0].src, e));
            }
        }, 100);
    }

    async loadShelfProducts(shelfId) {
        try {
            console.log(`Loading products for shelf ${shelfId}...`);

            // Add timeout to prevent hanging requests
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

            const response = await fetch(`/api/shelves/${shelfId}/products`, {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            clearTimeout(timeoutId);
            console.log(`Products API response status: ${response.status}`);

            if (!response.ok) {
                console.warn(`Failed to load products for shelf ${shelfId}: ${response.status} - ${response.statusText}`);
                // Try to get error details from response
                try {
                    const errorData = await response.json();
                    console.warn('Error details:', errorData);
                } catch (e) {
                    console.warn('Could not parse error response');
                }
                return [];
            }

            let productsData;
            try {
                productsData = await response.json();
            } catch (parseError) {
                console.error(`Failed to parse JSON response for shelf ${shelfId}:`, parseError);
                return [];
            }

            console.log(`Raw products data for shelf ${shelfId}:`, {
                type: typeof productsData,
                isArray: Array.isArray(productsData),
                isObject: typeof productsData === 'object',
                keys: typeof productsData === 'object' ? Object.keys(productsData) : null,
                length: Array.isArray(productsData) ? productsData.length : null
            });

            const processedProducts = productsData.data || productsData || [];

            // Validate and clean the products data
            const validatedProducts = processedProducts.filter(product => {
                if (!product || typeof product !== 'object') {
                    console.warn('Filtering out invalid product:', product);
                    return false;
                }
                return true;
            });

            console.log(`Validated products for shelf ${shelfId}:`, {
                originalCount: processedProducts.length,
                validatedCount: validatedProducts.length,
                sample: validatedProducts.length > 0 ? validatedProducts[0] : null
            });

            return validatedProducts;

        } catch (error) {
            if (error.name === 'AbortError') {
                console.error(`Request timeout loading products for shelf ${shelfId}`);
            } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                console.error(`Network error loading products for shelf ${shelfId}:`, error);
            } else {
                console.error(`Unexpected error loading products for shelf ${shelfId}:`, error);
            }
            return [];
        }
    }

    createShelfCard(shelf, products) {
        // Debug: Log products data for troubleshooting
        console.log(`Shelf: ${shelf.title || shelf.name} (${shelf.id})`, {
            productCount: products.length,
            sampleProduct: products.length > 0 ? products[0] : null,
            productsType: typeof products,
            productsIsArray: Array.isArray(products)
        });

        // Additional debug: Check if products have photo data
        if (products.length > 0) {
            const firstProduct = products[0];
            console.log('First product structure:', {
                keys: Object.keys(firstProduct),
                hasPhoto: 'photo' in firstProduct,
                photoKeys: firstProduct.photo ? Object.keys(firstProduct.photo) : null,
                photoMedium: firstProduct.photo?.medium || 'No medium image',
                photoLarge: firstProduct.photo?.large || 'No large image'
            });
        }

        const productCount = products.length;
        const productsHtml = products.length > 0
            ? products.slice(0, 6).map(product => this.createProductCard(product)).join('')
            : '<div class="col-12 text-center text-muted p-3">محصولی در این قفسه وجود ندارد</div>';

        console.log(`Generated products HTML length: ${productsHtml.length}`);
        console.log(`Products HTML preview:`, productsHtml.substring(0, 200));

        // Parse the HTML to check for images
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = productsHtml;
        const imgElements = tempDiv.querySelectorAll('img');
        const placeholderElements = tempDiv.querySelectorAll('.product-image-placeholder');

        console.log(`Found ${imgElements.length} img elements and ${placeholderElements.length} placeholders in generated HTML`);

        if (imgElements.length > 0) {
            console.log('First img element:', {
                src: imgElements[0].src,
                alt: imgElements[0].alt,
                outerHTML: imgElements[0].outerHTML
            });
        }
        
        const moreProductsText = products.length > 6 
            ? `<div class="col-12 text-center mt-2"><small class="text-muted">... و ${products.length - 6} محصول دیگر</small></div>`
            : '';

        const shelfHtml = `
            <div class="shelf-card fade-in">
                <div class="shelf-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="mb-1">
                                <i class="fas fa-box ms-2"></i>
                                ${shelf.title || shelf.name || 'قفسه بدون نام'}
                            </h5>
                            <small class="opacity-75">
                                <i class="fas fa-cubes ms-1"></i>
                                ${productCount} محصول
                            </small>
                        </div>
                        <button class="btn btn-light btn-sm" onclick="app.openUpdateModal(${shelf.id})">
                            <i class="fas fa-edit ms-1"></i>
                            بروزرسانی همه
                        </button>
                    </div>
                </div>

                <div class="product-grid">
                    ${productsHtml}
                    ${moreProductsText}
                </div>
            </div>
        `;

        console.log(`Final shelf HTML for ${shelf.title || shelf.name}:`, shelfHtml);

        return shelfHtml;
    }

    createProductCard(product) {
        try {
            // Validate product data
            if (!product || typeof product !== 'object') {
                console.error('Invalid product data:', product);
                return this.createErrorCard('Invalid product data');
            }

            // Try different image sources in order of preference
            const imageUrl = (product.photo?.medium || '').trim() ||
                            (product.photo?.large || '').trim() ||
                            (product.photo?.small || '').trim() ||
                            (product.photo?.extra_small || '').trim() ||
                            (product.image || '').trim() ||
                            (product.images?.[0] || '').trim() ||
                            '';

            const title = (product.title || product.name || 'محصول بدون نام').trim();
            const price = product.price && !isNaN(product.price)
                ? `${product.price.toLocaleString()} تومان`
                : 'قیمت موجود نیست';

            const productId = product.id || 'unknown';

            // Debug: Log image extraction for troubleshooting
            console.log(`Product: ${title} (${productId})`, {
                photo: product.photo,
                imageUrl: imageUrl,
                hasImage: !!imageUrl,
                price: product.price
            });

            // Create image HTML with better error handling
            let imageHtml = '';
            if (imageUrl && this.isValidImageUrl(imageUrl)) {
                imageHtml = `<img src="${imageUrl}"
                                 alt="${title}"
                                 class="product-image"
                                 data-product-id="${productId}"
                                 loading="lazy"
                                 onerror="handleImageError(this)"
                                 onload="handleImageLoad(this)">`;
            } else {
                imageHtml = `<div class="product-image-placeholder" data-product-id="${productId}">
                                <i class="fas fa-image fa-2x text-muted"></i>
                                <small class="text-muted mt-1">تصویر موجود نیست</small>
                             </div>`;
            }

            return `
                <div class="product-card" data-product-id="${productId}">
                    ${imageHtml}
                    <div class="product-title">${title}</div>
                    <div class="product-price">${price}</div>
                </div>
            `;

        } catch (error) {
            console.error('Error creating product card:', error, product);
            return this.createErrorCard('Error loading product');
        }
    }

    // Helper method to validate image URLs
    isValidImageUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
        } catch (e) {
            return false;
        }
    }

    // Helper method to create error cards
    createErrorCard(message) {
        return `
            <div class="product-card error-card">
                <div class="product-image-placeholder error-placeholder">
                    <i class="fas fa-exclamation-triangle fa-2x text-warning"></i>
                    <small class="text-muted mt-1">${message}</small>
                </div>
                <div class="product-title text-muted">${message}</div>
                <div class="product-price text-muted">—</div>
            </div>
        `;
    }

    openUpdateModal(shelfId) {
        this.currentShelfId = shelfId;
        const modal = new bootstrap.Modal(document.getElementById('updateModal'));
        modal.show();
        
        // Reset forms
        this.resetUpdateForms();
    }

    resetUpdateForms() {
        document.getElementById('descriptionForm').classList.add('d-none');
        document.getElementById('imageForm').classList.add('d-none');
        document.getElementById('updateDescriptionForm').reset();
        document.getElementById('updateImageForm').reset();
    }

    async handleDescriptionUpdate(e) {
        e.preventDefault();
        
        if (!this.currentShelfId) {
            this.showAlert('Error: No shelf selected', 'danger');
            return;
        }

        const formData = new FormData(e.target);
        const description = formData.get('description');
        
        if (!description.trim()) {
            this.showAlert('لطفاً توضیحاتی وارد کنید', 'warning');
            return;
        }

        this.showLoading(true);

        console.log('Starting description update:', {
            shelfId: this.currentShelfId,
            description: description,
            formDataEntries: Array.from(formData.entries())
        });

        try {
            const response = await fetch(`/api/shelves/${this.currentShelfId}/update-descriptions`, {
                method: 'POST',
                body: formData
            });

            console.log('Description update response:', {
                status: response.status,
                statusText: response.statusText,
                headers: Object.fromEntries(response.headers.entries())
            });

            const result = await response.json();
            console.log('Description update result:', result);

            if (response.ok && result.success) {
                this.showUpdateResults(result, 'description');
                this.hideModal('updateModal');
                await this.refreshData();
            } else {
                throw new Error(result.detail || 'Failed to update descriptions');
            }
        } catch (error) {
            console.error('Error updating descriptions:', error);
            this.showAlert(`خطا در بروزرسانی توضیحات: ${error.message}`, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    async handleImageUpdate(e) {
        e.preventDefault();
        
        if (!this.currentShelfId) {
            this.showAlert('Error: No shelf selected', 'danger');
            return;
        }

        const formData = new FormData(e.target);
        const imageFile = formData.get('image');
        
        if (!imageFile || imageFile.size === 0) {
            this.showAlert('لطفاً یک فایل تصویری انتخاب کنید', 'warning');
            return;
        }

        this.showLoading(true);
        
        try {
            const response = await fetch(`/api/shelves/${this.currentShelfId}/update-images`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showUpdateResults(result, 'image');
                this.hideModal('updateModal');
                await this.refreshData();
            } else {
                throw new Error(result.detail || 'Failed to update images');
            }
        } catch (error) {
            console.error('Error updating images:', error);
            this.showAlert(`Error updating images: ${error.message}`, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    showUpdateResults(result, updateType) {
        const modal = new bootstrap.Modal(document.getElementById('reviewModal'));
        const content = document.getElementById('reviewContent');
        
        const successCount = result.updated_count || 0;
        const failedCount = result.failed_count || 0;
        const totalCount = successCount + failedCount;
        
        content.innerHTML = `
            <div class="text-center mb-4">
                <i class="fas fa-chart-pie fa-3x text-primary mb-3"></i>
                <h4>Update Summary</h4>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="stats-card success">
                        <div class="icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <h3>${successCount}</h3>
                        <p>Successfully Updated</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card warning">
                        <div class="icon">
                            <i class="fas fa-exclamation-triangle"></i>
                        </div>
                        <h3>${failedCount}</h3>
                        <p>Failed Updates</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stats-card info">
                        <div class="icon">
                            <i class="fas fa-cubes"></i>
                        </div>
                        <h3>${totalCount}</h3>
                        <p>Total Products</p>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-${successCount > 0 ? 'success' : 'warning'}">
                <i class="fas fa-info-circle me-2"></i>
                <strong>Update Type:</strong> ${updateType === 'description' ? 'Product Descriptions' : 'Product Images'}
                <br>
                <strong>Success Rate:</strong> ${totalCount > 0 ? Math.round((successCount / totalCount) * 100) : 0}%
            </div>
            
            ${failedCount > 0 ? `
                <div class="alert alert-warning">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Failed Updates:</h6>
                    <p>Some products could not be updated. This might be due to permission issues or API limitations.</p>
                </div>
            ` : ''}
        `;
        
        modal.show();
    }

    showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert at top of main container
        const container = document.querySelector('main.container');
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.remove('d-none');
        } else {
            overlay.classList.add('d-none');
        }
    }

    hideModal(modalId) {
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        if (modal) {
            modal.hide();
        }
    }

    async refreshData() {
        if (window.location.pathname === '/dashboard') {
            this.showLoading(true);
            await this.loadDashboardData();
            this.showLoading(false);
            this.showAlert('Data refreshed successfully', 'success');
        }
    }
}

// Global functions for HTML onclick events
function showDescriptionUpdate() {
    document.getElementById('descriptionForm').classList.remove('d-none');
    document.getElementById('imageForm').classList.add('d-none');
}

function showImageUpdate() {
    document.getElementById('imageForm').classList.remove('d-none');
    document.getElementById('descriptionForm').classList.add('d-none');
}

function refreshData() {
    app.refreshData();
}

// Global image error handler
function handleImageError(img) {
    const productId = img.dataset.productId || 'unknown';
    console.error('Image failed to load:', {
        src: img.src,
        alt: img.alt,
        productId: productId,
        error: 'Image load failed'
    });

    // Replace failed image with enhanced placeholder
    img.outerHTML = `<div class="product-image-placeholder failed-image" data-product-id="${productId}">
                        <i class="fas fa-image fa-2x text-muted"></i>
                        <small class="text-muted mt-1">بارگذاری تصویر ناموفق</small>
                     </div>`;
}

// Global image load handler
function handleImageLoad(img) {
    const productId = img.dataset.productId || 'unknown';
    console.log('Image loaded successfully:', {
        src: img.src,
        alt: img.alt,
        productId: productId,
        dimensions: `${img.naturalWidth}x${img.naturalHeight}`
    });

    // Add success indicator
    img.classList.add('image-loaded');
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BasalamApp();
});
