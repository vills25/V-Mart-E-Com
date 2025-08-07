
from django.urls import path

# Admin
from myapp.views.admin.views import *

# Authentication (Login, SMTP email, Forgot/Reset Password)
from myapp.views.auth.authentication import *

# Buyers
from myapp.views.buyers.views import *

# Seller
from myapp.views.sellers.views import *

# Cart & Wishlist
from myapp.views.cart_wishlist.cart import *
from myapp.views.cart_wishlist.wishlist import *

# Orders
from myapp.views.orders.views import *
from myapp.views.orders.refunds import *

# Products
from myapp.views.products.categories import *
from myapp.views.products.subcategories import *
from myapp.views.products.reviews import *
from myapp.views.products.views import *


urlpatterns = [
    path('seller_register/',register_seller),
    path('update_seller/', update_seller),
    path('seller_delete/', seller_delete),

    path('buyer_register/',register_buyer),
    path('update_buyer/', update_buyer),
    path('buyer_delete/', buyer_delete),

    path('login/', login),
    path('logout_view/', logout_view),
    path('forgot_password_sent_email/', forgot_password_sent_email),
    path('reset_password/', reset_password),
  
    path('all_buyers_view_by_admin/', admin_all_buyers),
    path('all_sellers_view_by_admin/', admin_all_sellers),
    path('buyer_profile_with_orders/', buyer_profile_with_orders),
    path('seller_profile_with_products_orders/', seller_profile_with_products_orders),
    
    path('category_get/', category_get),
    path('category_create/', category_create),
    path('category_update/', category_update), 
    path('category_delete/', category_delete),

    path('sub_category_get/', subcategory_get),
    path('sub_category_create/', subcategory_create),
    path('sub_category_update/', subcategory_update),
    path('subcategory_delete/', subcategory_delete),

    path('product_search/', product_search),
    path('product_get/', product_get),
    path('product_create/', product_create),
    path('product_update/', product_update),
    path('product_delete/', product_delete),
    
    path('cart_get/', cart_get),
    path('cart_create/', cart_create),
    path('cart_delete/', cart_delete),
    path('cart_items_update/', cart_items_update),

    path('create_order/', create_order),
    path('order_list/', order_list), # Buyer can view his order details
    path('seller_order_list/', seller_order_list),
    path('update_order_status/', update_order_status),
    path('cancel_order_and_refund/', cancel_order_and_refund),
    path('update_refund_status/', update_refund_status),

    path('create_review/', create_review),
    path('update_review/', update_review),
    path('delete_review/', delete_review),

    path('wishlist_create/', wishlist_create),
    path('wishlist_remove/', wishlist_remove),

]