# from django.urls import path
# from .views import *

# urlpatterns = [
#     path('register/',register_buyer ),
#     path('login/', login_buyer),
#     path('logout/', logout_view),
#     path('forgotpassword/',forgot_password_view ),

#     path('buyerprofileview/',show_buyer_profile ),
#     # path('buyerupdate/', buyer_update),
#     path('buyerdelete/',buyer_delete ),
#     path('get_all_buyer/', get_all_buyers),

#     path('categorycreate/', category_create),
#     path('categoryview/',category_view ),
#     path('categoryupdate/',category_update ),
#     path('categorydelete/',category_delete ),

#     path('subcategorycreate/',subcategory_create ),
#     path('subcategoryview/',subcategory_view ),
#     path('subcategoryupdate/',subcategory_update ),
#     path('subcategorydelete/', subcategory_delete),

#     path('productcreate/',product_create),
#     path('productget/', product_get),
#     path('productupdate/',product_update ),
#     path('productdelete/',product_delete ),

#     # path('cartadd/',cart_create),
#     # path('cartget/', cart_get),
#     # path('cartupdate/', cart_update_delete),
#     path('cartdelete/', cart_delete),

#     path('cartitemsget/', cart_items_get),
#     path('cartitemscreate/', cart_items_create),
#     path('cartitemsupdate/', cart_items_update),
#     path('cartitemsdelete/', cart_items_delete),

#     path('cancelorder/', cancel_order),
#     # path('getallorders/', grt_all_orders_view),
#     path('checkout/', checkout_order),
    
#     # path('searchbuyer/', search_buyer),
#     # path('searchcategory/', search_category),
#     # path('searchsubcategory/', search_subcategory),
#     # path('searchproduct/', search_product),
#     # path('searchcartitems/', search_cart_items),
    
#     path('wishlistview/', whishlist_get),
#     path('wishlistadd/', whishlist_create),
#     path('wishlistremove/', whishlist_remove)
    
# ]

from django.urls import path
from .views import *

urlpatterns = [
    path('seller_register/',register_seller),
    path('update_seller/', update_seller),
    path('buyer_register/',register_buyer),
    path('update_buyer/', update_buyer),
    

    path('login/', login),
    path('logout_view/', logout_view),
    path('forgot_password/', forgot_password),
  
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
    path('order_list/', order_list),
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