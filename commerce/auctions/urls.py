from django.urls import path

from . import views

urlpatterns = [
    #Home Page 
    path("", views.index, name="index"),
    #User Authentication
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    #Categories
    path("categories/", views.categories_view, name="categories_view"),
    path("categories/<str:category_name>/",views.category_listings, name="category_listings"),
    #Listings
    path("create_listing/", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>/",views.listing_detail, name="listing_detail"),
    #Bidding
    path("bid/<int:listing_id>/",views.place_bid, name="place_bid"),
    #Auction management
    path("close_auction/<int:listing_id>/",views.close_auction, name="close_auction"),
    #Comments
    path("add_comment/<int:listing_id>/",views.add_comment, name="add_comment"),
    # Watchlist Management
    path("watchlist/", views.watchlist_view, name="watchlist_view"),
    path("add_to_watchlist/<int:listing_id>",views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>/",views.remove_from_watchlist, name="remove_from_watchlist")
    
    
    
    
    
]
