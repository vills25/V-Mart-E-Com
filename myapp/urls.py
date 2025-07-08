from django.urls import path
from .views import *

urlpatterns = [
    path('register/',register_view ),
    path('login/', login_view),
    path('buyerprofileview',buyer_profile_view ),
    path('buyerupdate/', buyer_update),
    path('buyerdelete/',buyer_delete ),
    path('passwordreset/',reset_password_view ),
    path('categorycreate/', category_create),
    path('categoryview/',category_view ),
    path('categoryupdate/',category_update ),
    path('categorydelete/',category_delete ),
    path('subcategorycreate/',subcategory_create ),
    path('subcategoryview/',subcategory_view ),
    path('subcategoryupdate/',subcategory_update_delete ),
    path('subcategorydelete/', subcategory_update_delete),
    path('productcreate/',product_create),
    path('productget/', product_get),
    path('productupdate/',product_update ),
    path('productdelete/',product_delete ),
    path('cartadd/',cart_create),
    path('cartget/', cart_get),
    path('cartupdate/', cart_update_delete),
    path('cartdelete/', cart_update_delete),
    path('cartitemsget/', cart_items_get),
    path('cartitemscreate/', cart_items_create),
    path('cartitemsupdate/', cart_items_update_delete),
    path('cartitemsdelete/', cart_items_update_delete),
    path('cancelorder/', cancel_order),
    path('getallorders', grt_all_orders_view),
    path('checkout/', checkout_view)

]